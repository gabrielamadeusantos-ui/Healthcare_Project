# src/utils.py
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

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
    Returns a dictionary mapping file names to their full metadata (id, mimeType, modifiedTime).
    Handles pagination in case the folder contains many files.
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
            files_dict[f['name']] = f
            
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
            
    return files_dict