# src/main.py
import sys
import os
from datetime import datetime
import logging

# (Optional) If you need to add src to sys.path, uncomment the line below.
# sys.path.append(os.path.dirname(__file__))

# Import our own modules – using relative imports since they're in the same package
from .config import SOURCE_FOLDER_ID, DESTINATION_FOLDER_ID, SUFFIX
from .utils import authenticate, list_files
from .extract import extract_file
from .transform import transform_data
from .load import load_file

# Set up logging – cleaner than print statements and we can adjust verbosity later
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ==========================================
# VISUAL INTERFACE (kept for compatibility)
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
    """Print a fancy title with a border – makes the console output more readable."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*50}\n{text.center(50)}\n{'='*50}{Colors.END}")

# ==========================================
# ETL ORCHESTRATOR
# ==========================================
def run_pipeline():
    """
    Main orchestration function:
      1. Authenticate with Google Drive.
      2. List all files in the source and destination folders.
      3. For each file in the source, decide whether to process it based on:
         - whether it already exists in dest,
         - its modification timestamp,
         - or a manual 'force' flag.
      4. Extract, transform, and load (update or create) each file.
    """
    service = authenticate()
    print_title("ETL SYSTEM - MONTHLY SYNCHRONIZATION")

    # Ask the user if they want to ignore timestamps and reprocess everything
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

    # Loop through each file in the source
    for original_name, source_info in source_files.items():
        base_name, extension = os.path.splitext(original_name)
        processed_name = f"{base_name}{SUFFIX}{extension}"

        dt_source = datetime.fromisoformat(source_info['modifiedTime'].replace('Z', '+00:00')).timestamp()
        
        process_file = False
        status_msg = ""

        # Decide whether we need to process this file
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

        # Execute the full ETL if needed
        if process_file:
            try:
                print(f"   🛠️  Processing: {processed_name}...", end="\r")
                
                raw_buffer = extract_file(service, source_info)
                processed_buffer = transform_data(raw_buffer, original_name)
                load_file(service, processed_buffer, processed_name, DESTINATION_FOLDER_ID, destination_files)
                
                print(f"   ✅ {Colors.GREEN}Finished: {processed_name}           {Colors.END}")
            except Exception as e:
                # Catch any error so the pipeline continues with the next file
                print(f"   ❌ {Colors.FAIL}Critical Error: {str(e)}{Colors.END}")

if __name__ == '__main__':
    run_pipeline()
    print_title("PROCESS FINISHED")