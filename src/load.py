# src/load.py
from googleapiclient.http import MediaIoBaseUpload
import mimetypes
import re
from datetime import datetime  # <-- ADICIONADO

def sanitize_filename(name: str) -> str:
    """
    Strip out characters that might cause trouble in Google Drive filenames.
    We keep only letters, digits, spaces, underscores, hyphens, and dots.
    """
    return re.sub(r'[^\w\-_. ]+', '_', name)

def load_file(service, buffer, file_name, destination_folder_id, destination_files):
    """
    Upload (or update) a file to Google Drive.
    If a file with the same name already exists in the destination folder,
    we update it instead of creating a duplicate – that way we avoid clutter.
    The `destination_files` dictionary is updated in-place to reflect the new/updated file,
    so subsequent calls see the most up-to-date state.
    """
    
    file_name = sanitize_filename(file_name)
    
    # Safety check: make sure the buffer actually has data before uploading
    buffer.seek(0, 2)  # move to end
    size = buffer.tell()
    buffer.seek(0)
    if size == 0:
        raise ValueError("Buffer is empty – refusing to upload an empty file")
    
    # Guess the MIME type from the file extension; fallback to generic binary
    mime_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
    media = MediaIoBaseUpload(buffer, mimetype=mime_type, resumable=True)

    # If the file already exists in the target folder, update it
    if file_name in destination_files:
        file_id = destination_files[file_name]['id']
        service.files().update(
            fileId=file_id, 
            media_body=media,
            supportsAllDrives=True  # needed if we're working with shared drives
        ).execute()
        # Update the modifiedTime in our local dictionary to reflect the new version
        # (The API does not return the new modifiedTime in the update response, so we set it to now)
        destination_files[file_name]['modifiedTime'] = datetime.now().isoformat() + 'Z'
    else:
        # Otherwise, create a new file in the destination folder
        body = {'name': file_name, 'parents': [destination_folder_id]}
        result = service.files().create(
            body=body, 
            media_body=media,
            supportsAllDrives=True,
            fields='id, mimeType, modifiedTime'  # request these fields back
        ).execute()
        # Add the new file's metadata to the dictionary so future updates find it
        destination_files[file_name] = {
            'id': result['id'],
            'mimeType': result.get('mimeType', 'application/octet-stream'),
            'modifiedTime': result.get('modifiedTime', datetime.now().isoformat() + 'Z')
        }