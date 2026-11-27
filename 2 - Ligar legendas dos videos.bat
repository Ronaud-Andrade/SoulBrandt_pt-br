@echo off
chcp 65001 >nul
title Traducao PT-BR de Demon's Souls - ligar legendas
cd /d "%~dp0"
set "PACOTE="
if exist "%~dp0PT-BR\python\python.exe" set "PACOTE=%~dp0PT-BR"
if not defined PACOTE if exist "%~dp0..\PT-BR\python\python.exe" set "PACOTE=%~dp0..\PT-BR"
if defined PACOTE goto :temos_pacote
echo Nao achei a pasta PT-BR da traducao. Rode primeiro o "1 - Instalar traducao PT-BR.bat".
pause
exit /b 1
:temos_pacote
"%PACOTE%\python\python.exe" -I "%~dp0converter_ptbr_mod.py" legendas --pacote "%PACOTE%"
echo.
pause
