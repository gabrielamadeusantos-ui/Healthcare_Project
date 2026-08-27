# src/config.py
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

SOURCE_FOLDER_ID = os.getenv('SOURCE_FOLDER_ID')
DESTINATION_FOLDER_ID = os.getenv('DESTINATION_FOLDER_ID')
SUFFIX = os.getenv('SUFFIX', '_PROCESSED')

CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH', 'credentials.json')
TOKEN_PATH = os.getenv('TOKEN_PATH', 'token.json')

CREDENTIALS_PATH = os.path.join(BASE_DIR, CREDENTIALS_PATH)
TOKEN_PATH = os.path.join(BASE_DIR, TOKEN_PATH)

# Caminho para o arquivo de lock (garante execução única)
LOCK_FILE = os.path.join(BASE_DIR, 'etl.lock')

if not SOURCE_FOLDER_ID or not DESTINATION_FOLDER_ID:
    raise EnvironmentError("SOURCE_FOLDER_ID and DESTINATION_FOLDER_ID must be defined in .env")