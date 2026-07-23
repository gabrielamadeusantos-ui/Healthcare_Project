import io
from googleapiclient.http import MediaIoBaseDownload

# Map to handle spreadsheets created directly in Google Drive
EXPORT_MAP = {
    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

def extract_file(service, file_info):
    """Downloads file content to a RAM buffer, converting native Google formats if necessary."""
    file_id = file_info['id']
    mime = file_info['mimeType']
    buffer = io.BytesIO()
    
    # Export Google Workspace files to standard formats
    if mime in EXPORT_MAP:
        req = service.files().export_media(fileId=file_id, mimeType=EXPORT_MAP[mime])
    else:
        req = service.files().get_media(fileId=file_id)
        
    downloader = MediaIoBaseDownload(buffer, req)
    
    done = False
    while not done:
        _, done = downloader.next_chunk()
    
    buffer.seek(0)
    return buffer