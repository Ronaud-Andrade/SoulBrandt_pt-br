@echo off
chcp 65001 >nul
title Traducao PT-BR de Demon's Souls - instalar
cd /d "%~dp0"
set "PACOTE="
if exist "%~dp0PT-BR\python\python.exe" set "PACOTE=%~dp0PT-BR"
if not defined PACOTE if exist "%~dp0..\PT-BR\python\python.exe" set "PACOTE=%~dp0..\PT-BR"
if defined PACOTE goto :temos_pacote
echo Baixando a traducao do StarKillerChief - PT-BR-Soulbrandt.zip, uns 18 MB...
set "DESTINO=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol='Tls12'; $zip=Join-Path $env:DESTINO 'PT-BR-Soulbrandt.zip'; Invoke-WebRequest -UseBasicParsing -Uri 'https://github.com/StarKillerChief/demons-souls-pt-br/releases/latest/download/PT-BR-Soulbrandt.zip' -OutFile $zip; Expand-Archive -Force -LiteralPath $zip -DestinationPath $env:DESTINO; Remove-Item -LiteralPath $zip"
if exist "%~dp0PT-BR\python\python.exe" set "PACOTE=%~dp0PT-BR"
if defined PACOTE goto :temos_pacote
echo.
echo Nao consegui baixar a traducao. Baixe o PT-BR-Soulbrandt.zip em
echo https://github.com/StarKillerChief/demons-souls-pt-br/releases
echo e extraia ele nesta pasta, para ficar uma pasta PT-BR aqui dentro. Depois rode este arquivo de novo.
pause
exit /b 1
:temos_pacote
echo.
echo Qual fonte voce quer?
echo   1 = Fontes HD - letras novas e nitidas, recomendado
echo   2 = Fontes originais do jogo, como no PS3
choice /c 12 /n /m "Digite 1 ou 2: "
if errorlevel 2 (set "FONTES=original") else (set "FONTES=hd")
echo.
echo Ligar tambem as legendas dos videos?
echo   Elas usam uma DLL ao lado do Soulbrandt.exe e cada atualizacao do Soulbrandt desliga;
echo   depois e so rodar o "2 - Ligar legendas dos videos.bat".
choice /c SN /n /m "S ou N: "
if errorlevel 2 (set "LEGENDAS=") else (set "LEGENDAS=--legendas")
echo.
"%PACOTE%\python\python.exe" -I "%~dp0converter_ptbr_mod.py" instalar --fontes %FONTES% %LEGENDAS% --pacote "%PACOTE%"
echo.
pause
