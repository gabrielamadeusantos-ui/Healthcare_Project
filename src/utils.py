# src/utils.py
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

from .config import CREDENTIALS_PATH, TOKEN_PATH

SCOPES = ['https://www.googleapis.com/auth/drive']

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
    Retorna um dicionário {nome: metadados} com apenas o arquivo mais recente
    para cada nome (evita chaves duplicadas).
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
            
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
            
    return files_dict

def get_files_by_name(service, folder_id, name):
    """
    Retorna uma lista de todos os arquivos (não trash) na pasta com o nome exato.
    Útil para localizar duplicatas.
    """
    # Escape aspas simples no nome para segurança
    safe_name = name.replace("'", "\\'")
    query = f"'{folder_id}' in parents and name='{safe_name}' and trashed=false"
    files = []
    page_token = None
    while True:
        response = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            pageToken=page_token
        ).execute()
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return files