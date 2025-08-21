@echo off
REM Ruta completa al intérprete de Python
SET PYTHON_PATH="C:\Users\Taboa\AppData\Local\Microsoft\WindowsApps\python.exe"

REM Ruta completa al directorio de tu script main.py
SET SCRIPT_DIR="C:\Users\Taboa\Desktop\Sombrero_No_Tan_Sabio\code"

REM Cambiar al directorio del script
cd /d %SCRIPT_DIR%

REM Ejecutar el script de Python
start "" %PYTHON_PATH% "test.py"