# src/load.py
from googleapiclient.http import MediaIoBaseUpload
import mimetypes
import re
from datetime import datetime

from .utils import get_files_by_name  # <-- nova função auxiliar

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-_. ]+', '_', name)

def load_file(service, buffer, file_name, destination_folder_id, destination_files):
    """
    Upload (ou atualiza) um arquivo no Drive.
    Se já existir um arquivo com esse nome, atualiza o mais recente e
    **exclui todos os outros** com o mesmo nome (remove duplicatas).
    O dicionário `destination_files` é atualizado em memória.
    """
    file_name = sanitize_filename(file_name)
    
    # Verifica se o buffer não está vazio
    buffer.seek(0, 2)
    size = buffer.tell()
    buffer.seek(0)
    if size == 0:
        raise ValueError("Buffer vazio – recusando upload.")
    
    mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
    media = MediaIoBaseUpload(buffer, mimetype=mime_type, resumable=True)

    # Busca TODOS os arquivos com esse nome na pasta (inclusive duplicatas)
    all_files = get_files_by_name(service, destination_folder_id, file_name)

    if all_files:
        # Ordena por modifiedTime (mais recente primeiro)
        all_files.sort(
            key=lambda f: datetime.fromisoformat(f['modifiedTime'].replace('Z', '+00:00')),
            reverse=True
        )
        # O primeiro é o mais recente – atualizamos ele
        latest = all_files[0]
        file_id = latest['id']
        service.files().update(
            fileId=file_id,
            media_body=media,
            supportsAllDrives=True
        ).execute()

        # Atualiza o dicionário local com os novos metadados
        destination_files[file_name] = {
            'id': file_id,
            'mimeType': latest.get('mimeType', 'application/octet-stream'),
            'modifiedTime': datetime.now().isoformat() + 'Z'  # aproximado
        }

        # Exclui os demais (duplicatas antigas)
        for dup in all_files[1:]:
            try:
                service.files().delete(fileId=dup['id'], supportsAllDrives=True).execute()
                print(f"   🗑️  Duplicata removida: {dup['name']} (ID: {dup['id']})")
            except Exception as e:
                print(f"   ⚠️  Não foi possível deletar duplicata {dup['id']}: {e}")
    else:
        # Nenhum arquivo com esse nome – cria novo
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