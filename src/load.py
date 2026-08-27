# src/load.py
import logging
from googleapiclient.http import MediaIoBaseUpload
import mimetypes
import re
from datetime import datetime

from .utils import get_all_files_by_name

logger = logging.getLogger(__name__)

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-_. ]+', '_', name)

def load_file(service, buffer, file_name, destination_folder_id, destination_files):
    """
    Upload ou atualiza um arquivo no Drive.
    Se houver múltiplos arquivos com o mesmo nome, atualiza o mais recente e
    exclui todos os outros (elimina duplicatas).
    """
    file_name = sanitize_filename(file_name)
    logger.info(f"📤 Carregando '{file_name}'...")

    # Verifica se o buffer não está vazio
    buffer.seek(0, 2)
    size = buffer.tell()
    buffer.seek(0)
    if size == 0:
        raise ValueError("Buffer vazio – recusando upload.")

    mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
    media = MediaIoBaseUpload(buffer, mimetype=mime_type, resumable=True)

    # Busca TODOS os arquivos com esse nome na pasta
    all_files = get_all_files_by_name(service, destination_folder_id, file_name)
    logger.info(f"🔍 Encontrados {len(all_files)} arquivo(s) com o nome '{file_name}' na pasta de destino.")

    if all_files:
        # Ordena por modifiedTime (mais recente primeiro)
        all_files.sort(
            key=lambda f: datetime.fromisoformat(f['modifiedTime'].replace('Z', '+00:00')),
            reverse=True
        )
        latest = all_files[0]
        file_id = latest['id']
        logger.info(f"🔄 Atualizando arquivo existente: {file_name} (ID: {file_id})")

        # Atualiza o mais recente
        service.files().update(
            fileId=file_id,
            media_body=media,
            supportsAllDrives=True
        ).execute()

        # Atualiza o dicionário local
        destination_files[file_name] = {
            'id': file_id,
            'mimeType': latest.get('mimeType', 'application/octet-stream'),
            'modifiedTime': datetime.now().isoformat() + 'Z'
        }

        # Exclui as duplicatas antigas (todas exceto a mais recente)
        for dup in all_files[1:]:
            try:
                service.files().delete(fileId=dup['id'], supportsAllDrives=True).execute()
                logger.info(f"🗑️  Duplicata removida: {dup['name']} (ID: {dup['id']})")
            except Exception as e:
                logger.warning(f"⚠️  Não foi possível deletar duplicata {dup['id']}: {e}")
    else:
        # Nenhum arquivo com esse nome – cria novo
        logger.info(f"✨ Criando novo arquivo: {file_name}")
        body = {'name': file_name, 'parents': [destination_folder_id]}
        result = service.files().create(
            body=body,
            media_body=media,
            supportsAllDrives=True,
            fields='id, mimeType, modifiedTime'
        ).execute()
        destination_files[file_name] = {
            'id': result['id'],
            'mimeType': result.get('mimeType', 'application/octet-stream'),
            'modifiedTime': result.get('modifiedTime', datetime.now().isoformat() + 'Z')
        }