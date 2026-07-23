@echo off
cd /d "%~dp0"

:: Create an file with the answser "n" (can be changed to "y" if it needed to force it)
echo n > answer.txt

:: execute the script
python -m src.main < answer.txt

:: Removes the temp file
del answer.txt