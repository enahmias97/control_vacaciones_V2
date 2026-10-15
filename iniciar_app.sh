#!/usr/bin/env bash
# Arranca la app desde SU carpeta (Git Bash / Mac / Linux).
# Así Streamlit encuentra .streamlit/config.toml y la carpeta data/.
cd "$(dirname "$0")" || exit 1
if [ -f ".venv/Scripts/activate" ]; then source .venv/Scripts/activate      # Windows
elif [ -f ".venv/bin/activate" ]; then source .venv/bin/activate            # Mac/Linux
else echo "No existe .venv. Sigue el paso 2 de PASO_A_PASO.md"; exit 1; fi
python -m streamlit run app.py
