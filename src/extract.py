# src/extract.py
import io
from googleapiclient.http import MediaIoBaseDownload

# Mapping for Google Workspace native files to standard formats
# This lets us download them as real .xlsx or .docx files
EXPORT_MAP = {
    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

def extract_file(service, file_info):
    """
    Download a file from Google Drive into an in-memory buffer.
    If the file is a Google Docs/Sheets native type, we export it to a standard format.
    Returns a BytesIO object ready to be read.
    """
    file_id = file_info['id']
    mime = file_info['mimeType']
    buffer = io.BytesIO()
    
    # Choose the appropriate download method: export for native, regular for others
    if mime in EXPORT_MAP:
        req = service.files().export_media(fileId=file_id, mimeType=EXPORT_MAP[mime])
    else:
        req = service.files().get_media(fileId=file_id)
        
    downloader = MediaIoBaseDownload(buffer, req)
    
    # Download in chunks (handles large files gracefully)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    
    # Rewind the buffer so the caller can read from the beginning
    buffer.seek(0)
    return buffer