@echo off
cd /d "%~dp0"
:: Запуск через интерпретатор из вашего виртуального окружения
start "" ".venv\Scripts\pythonw.exe" main.py
exit
