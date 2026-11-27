@echo off
chcp 65001 >nul
title Traducao PT-BR - desligar legendas
cd /d "%~dp0"
set "PY="
if exist "..\PT-BR\python\python.exe" set "PY=..\PT-BR\python\python.exe"
if not defined PY where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo Nao achei o Python. Coloque esta pasta ao lado da pasta PT-BR da traducao,
  echo dentro da pasta do Soulbrandt.exe, ou instale o Python 3.
  pause
  exit /b 1
)
%PY% -I "%~dp0converter_ptbr_mod.py" tirar-legendas %*
echo.
pause
