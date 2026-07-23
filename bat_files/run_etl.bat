@echo off
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%.."
python -m src.main
pause