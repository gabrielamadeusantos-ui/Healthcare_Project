# src/load.py
from googleapiclient.http import MediaIoBaseUpload
import mimetypes
import re

def sanitize_filename(name: str) -> str:
    """Remove caracteres problemáticos para nomes de arquivo no Drive."""
    return re.sub(r'[^\w\-_. ]+', '_', name)

def load_file(service, buffer, file_name, destination_folder_id, destination_files):
    """Uploads to Drive, deciding between Create or Update."""
    
    file_name = sanitize_filename(file_name)
    
    # Shielding: verifica se o buffer não está vazio
    buffer.seek(0, 2)  # vai para o final
    size = buffer.tell()
    buffer.seek(0)
    if size == 0:
        raise ValueError("Buffer vazio – não será feito upload")
    
    mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
    media = MediaIoBaseUpload(buffer, mimetype=mime_type, resumable=True)

    if file_name in destination_files:
        # Update existing file
        file_id = destination_files[file_name]['id']
        service.files().update(
            fileId=file_id, 
            media_body=media,
            supportsAllDrives=True
        ).execute()
    else:
        # Create new file
        body = {'name': file_name, 'parents': [destination_folder_id]}
        service.files().create(
            body=body, 
            media_body=media,
            supportsAllDrives=True
        ).execute()