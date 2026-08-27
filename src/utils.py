# src/utils.py
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

# Import the credential paths defined in config
from .config import CREDENTIALS_PATH, TOKEN_PATH

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    """
    Handle OAuth2 authentication for Google Drive.
    It looks for a stored token (token.json) – if valid, use it.
    If expired, refresh it (if a refresh token is available).
    Otherwise, launch a local server to get new authorization.
    Finally, save the new token for next time.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Write the updated credentials back to the token file
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def list_files(service, folder_id):
    """
    Retrieve all non-trashed files inside a given Google Drive folder.
    Returns a dictionary mapping file names to their metadata (id, mimeType, modifiedTime).
    If multiple files have the same name, only the MOST RECENTLY MODIFIED one is kept
    to avoid duplicate keys and to ensure we always update the latest version.
    Handles pagination.
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
            # If this name already exists, compare modifiedTime and keep the newest
            if name in files_dict:
                existing = files_dict[name]
                # Parse timestamps (they come in ISO 8601 format with 'Z')
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