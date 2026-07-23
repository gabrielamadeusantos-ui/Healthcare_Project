# src/config.py
import os
from dotenv import load_dotenv

# Define o caminho absoluto para a raiz do projeto (um nível acima de src)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Carrega o arquivo .env localizado na raiz
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

# IDs das pastas no Google Drive
SOURCE_FOLDER_ID = os.getenv('SOURCE_FOLDER_ID')
DESTINATION_FOLDER_ID = os.getenv('DESTINATION_FOLDER_ID')
SUFFIX = os.getenv('SUFFIX', '_PROCESSED')

# Caminhos para credenciais (podem ser relativos à raiz)
CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH', 'credentials.json')
TOKEN_PATH = os.getenv('TOKEN_PATH', 'token.json')

# Converte caminhos relativos para absolutos (baseados na raiz)
CREDENTIALS_PATH = os.path.join(BASE_DIR, CREDENTIALS_PATH)
TOKEN_PATH = os.path.join(BASE_DIR, TOKEN_PATH)

# Validação
if not SOURCE_FOLDER_ID or not DESTINATION_FOLDER_ID:
    raise EnvironmentError(
        "SOURCE_FOLDER_ID e DESTINATION_FOLDER_ID devem estar definidos no .env"
    )