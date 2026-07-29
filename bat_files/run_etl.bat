@echo off
:: Vai para a raiz do projeto
cd /d "%~dp0.."

echo Executando na pasta: %cd%
echo.
echo O script vai solicitar sua entrada (ex: "n" ou "y"). Digite e pressione Enter.
echo.

:: Executa sem redirecionar a entrada, permitindo interação do usuário
python -m src.main

:: Mantém a janela aberta após a execução para ver o resultado
echo.
echo Pressione qualquer tecla para fechar...
pause > nul