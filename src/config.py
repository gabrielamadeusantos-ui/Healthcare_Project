# src/config.py
import os
from dotenv import load_dotenv

# Determine the project root (one level above 'src')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from the .env file at the root
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

# Google Drive folder IDs – these must be set in .env
SOURCE_FOLDER_ID = os.getenv('SOURCE_FOLDER_ID')
DESTINATION_FOLDER_ID = os.getenv('DESTINATION_FOLDER_ID')
SUFFIX = os.getenv('SUFFIX', '_PROCESSED')

# Paths for OAuth credentials – can be relative to the root
CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH', 'credentials.json')
TOKEN_PATH = os.getenv('TOKEN_PATH', 'token.json')

# Convert to absolute paths so we don't depend on the current working directory
CREDENTIALS_PATH = os.path.join(BASE_DIR, CREDENTIALS_PATH)
TOKEN_PATH = os.path.join(BASE_DIR, TOKEN_PATH)

# Quick sanity check – better to fail early if these are missing
if not SOURCE_FOLDER_ID or not DESTINATION_FOLDER_ID:
    raise EnvironmentError(
        "SOURCE_FOLDER_ID and DESTINATION_FOLDER_ID must be defined in .env"
    )