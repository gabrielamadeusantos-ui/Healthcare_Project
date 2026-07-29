@echo off
:: 1. Vai para a RAIZ do projeto (sobe 1 nível de "bat_files" para "Healthcare_Project")
cd /d "%~dp0.."

:: 2. (Opcional) Exibe onde estamos para confirmar
echo Executando na pasta: %cd%

:: 3. Executa o ETL passando "n" automaticamente (sem criar arquivos temporários)
echo n | python -m src.main

:: 4. Se quiser pausar para ver o resultado ao dar duplo clique, descomente a linha abaixo:
:: pause