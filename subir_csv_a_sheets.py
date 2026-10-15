# -*- coding: utf-8 -*-
"""Sube UNA VEZ los CSV de data/ al Google Sheet configurado en
.streamlit/secrets.toml. Reemplaza el contenido de cada pestaña.

Uso (con el entorno virtual activo, desde la carpeta de la app):
    python subir_csv_a_sheets.py
"""
import os
import sys

import gspread
import pandas as pd

TABLAS = ["equipos", "empleados", "vacaciones", "feriados"]

RUTA = os.path.join(".streamlit", "secrets.toml")
try:
    import tomllib                                  # Python 3.11+
    with open(RUTA, "rb") as fh:
        sec = tomllib.load(fh)
except ImportError:
    import toml                                     # viene con Streamlit
    sec = toml.load(RUTA)
gc = gspread.service_account_from_dict(sec["gcp_service_account"])
libro = gc.open_by_key(sec["sheets"]["spreadsheet_id"])

faltan = [t for t in TABLAS if not os.path.exists(os.path.join("data", t + ".csv"))]
if faltan:
    sys.exit(f"No encuentro data/{faltan[0]}.csv. Ejecuta esto desde la carpeta de la app.")

if input("Esto REEMPLAZA las pestañas del Sheet con tus CSV. ¿Continuar? (si/no) ").strip().lower() != "si":
    sys.exit("Cancelado.")

for t in TABLAS:
    df = pd.read_csv(os.path.join("data", t + ".csv"), dtype=str,
                     keep_default_na=False, encoding="utf-8-sig")
    vals = [list(df.columns)] + df.astype(str).values.tolist()
    try:
        ws = libro.worksheet(t)
    except gspread.WorksheetNotFound:
        ws = libro.add_worksheet(title=t, rows=max(1000, len(vals) + 100),
                                 cols=max(10, len(df.columns)))
    if ws.row_count < len(vals):
        ws.add_rows(len(vals) - ws.row_count + 100)
    ws.clear()
    ws.update(values=vals, range_name="A1", value_input_option="RAW")
    print(f"  {t}: {len(df)} filas subidas")
print("Listo. Abre la app y revisa los datos.")
