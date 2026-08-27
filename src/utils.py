# src/utils.py
import os
import time
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

from .config import CREDENTIALS_PATH, TOKEN_PATH, LOCK_FILE

logger = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/drive']

def acquire_lock(timeout=60):
    """
    Tenta adquirir um lock exclusivo via arquivo.
    Retorna True se conseguiu, False se timeout.
    """
    start = time.time()
    while True:
        try:
            # Tenta criar o arquivo com modo exclusivo (falha se já existir)
            fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            logger.info("🔒 Lock adquirido com sucesso.")
            return True
        except FileExistsError:
            if time.time() - start > timeout:
                logger.error(f"⏰ Timeout ao tentar adquirir lock (>{timeout}s).")
                return False
            logger.warning("⏳ Lock ocupado, aguardando...")
            time.sleep(1)

def release_lock():
    """Remove o arquivo de lock."""
    try:
        os.remove(LOCK_FILE)
        logger.info("🔓 Lock liberado.")
    except OSError:
        pass

def authenticate():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def list_files(service, folder_id):
    """
    Retorna dicionário {nome: metadados} com apenas o arquivo mais recente para cada nome.
    """
    files_dict = {}
    query = f"'{folder_id}' in parents and trashed=false"
    page_token = None
    while True:
        response = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            pageToken=page_token
        ).execute()
        for f in response.get('files', []):
            name = f['name']
            if name in files_dict:
                existing = files_dict[name]
                existing_time = datetime.fromisoformat(existing['modifiedTime'].replace('Z', '+00:00'))
                new_time = datetime.fromisoformat(f['modifiedTime'].replace('Z', '+00:00'))
                if new_time > existing_time:
                    files_dict[name] = f
            else:
                files_dict[name] = f
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    return files_dict

def get_all_files_by_name(service, folder_id, target_name):
    """
    Retorna uma lista de TODOS os arquivos (não trash) na pasta com o nome exato.
    Em vez de usar filtro na query (que pode ter problemas com caracteres especiais),
    obtemos todos os arquivos da pasta e filtramos em memória.
    Isso é mais seguro e evita escapes complicados.
    """
    query = f"'{folder_id}' in parents and trashed=false"
    all_files = []
    page_token = None
    while True:
        response = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            pageToken=page_token
        ).execute()
        for f in response.get('files', []):
            if f['name'] == target_name:
                all_files.append(f)
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    return all_files