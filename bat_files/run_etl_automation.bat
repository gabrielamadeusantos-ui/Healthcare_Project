@echo off
:: Change to the project root directory (one level above the folder containing this .bat)
cd /d "%~dp0.."

:: Create a temporary file with the answer "n" (change to "y" if you want to force reprocessing)
echo n > answer.txt

:: Execute the ETL pipeline – now the 'src' module can be found because we are in the root
python -m src.main < answer.txt

:: Remove the temporary answer file
del answer.txt