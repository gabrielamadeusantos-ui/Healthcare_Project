# src/main.py
import sys
import os
from datetime import datetime
import logging

# Adiciona o diretório src ao sys.path (caso necessário)
# sys.path.append(os.path.dirname(__file__))

# Usa import relativo para módulos do mesmo pacote
from .config import SOURCE_FOLDER_ID, DESTINATION_FOLDER_ID, SUFFIX
from .utils import authenticate, list_files
from .extract import extract_file
from .transform import transform_data
from .load import load_file

# Configura logging (substitui os prints coloridos)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ==========================================
# VISUAL INTERFACE (opcional, mantido para compatibilidade)
# ==========================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_title(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*50}\n{text.center(50)}\n{'='*50}{Colors.END}")

# ==========================================
# ETL ORCHESTRATOR
# ==========================================
def run_pipeline():
    service = authenticate()
    print_title("ETL SYSTEM - MONTHLY SYNCHRONIZATION")

    print(f"{Colors.BOLD}Execution Configuration:{Colors.END}")
    answer = input(f"{Colors.BLUE}👉 Force reprocessing of ALL files? (y/n): {Colors.END}").strip().lower()
    force_reprocess = (answer == 'y')
    print("-" * 50)

    print("🔍 Analyzing files in the cloud...")
    source_files = list_files(service, SOURCE_FOLDER_ID)
    destination_files = list_files(service, DESTINATION_FOLDER_ID)

    if not source_files:
        print(f"{Colors.WARNING}No files found in the source folder.{Colors.END}")
        return

    for original_name, source_info in source_files.items():
        base_name, extension = os.path.splitext(original_name)
        processed_name = f"{base_name}{SUFFIX}{extension}"

        dt_source = datetime.fromisoformat(source_info['modifiedTime'].replace('Z', '+00:00')).timestamp()
        
        process_file = False
        status_msg = ""

        if processed_name in destination_files:
            dt_dest = datetime.fromisoformat(destination_files[processed_name]['modifiedTime'].replace('Z', '+00:00')).timestamp()
            
            if force_reprocess:
                status_msg = f"{Colors.WARNING}⚠️ Forced Reprocessing{Colors.END}"
                process_file = True
            elif dt_source > dt_dest:
                status_msg = f"{Colors.BLUE}🔄 Update detected (New source){Colors.END}"
                process_file = True
            else:
                status_msg = f"{Colors.WARNING}⏭️  Already processed previously{Colors.END}"
        else:
            status_msg = f"{Colors.GREEN}✨ New file identified{Colors.END}"
            process_file = True

        print(f"[{original_name}] -> {status_msg}")

        if process_file:
            try:
                print(f"   🛠️  Processing: {processed_name}...", end="\r")
                
                raw_buffer = extract_file(service, source_info)
                processed_buffer = transform_data(raw_buffer, original_name)
                load_file(service, processed_buffer, processed_name, DESTINATION_FOLDER_ID, destination_files)
                
                print(f"   ✅ {Colors.GREEN}Finished: {processed_name}           {Colors.END}")
            except Exception as e:
                print(f"   ❌ {Colors.FAIL}Critical Error: {str(e)}{Colors.END}")

if __name__ == '__main__':
    run_pipeline()
    print_title("PROCESS FINISHED")