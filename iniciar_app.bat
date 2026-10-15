@echo off
REM Arranca la app desde SU carpeta (doble clic o desde CMD/PowerShell).
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
  echo No existe .venv. Sigue el paso 2 de PASO_A_PASO.md
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"
python -m streamlit run app.py
pause
