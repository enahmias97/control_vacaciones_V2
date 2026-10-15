# Publicar en Streamlit Cloud con los datos en Google Sheets

**Resultado:** todo el equipo entra a un link `https://<tu-app>.streamlit.app`, y
lo que alguien guarda lo ven los demás en máximo 30 segundos. Los datos viven en
un Google Sheet, no en la app.

> Antes de empezar: son datos personales de empleados. Confirma con TI o con
> People que pueden guardarse en Google Drive y en Streamlit Cloud.

---

## Parte A · Google Cloud: crear la "cuenta robot" (una sola vez, unos 10 min)
1. Entra a https://console.cloud.google.com y crea un proyecto (ej. `vacaciones-wpp`).
2. Menú **APIs y servicios → Biblioteca**: busca y **habilita** las dos:
   - **Google Sheets API**
   - **Google Drive API**
3. **APIs y servicios → Credenciales → Crear credenciales → Cuenta de servicio**.
   Nombre: `vacaciones-app`. Termina el asistente sin asignar roles.
4. Abre la cuenta de servicio creada → pestaña **Claves → Agregar clave →
   Crear clave nueva → JSON**. Se descarga un archivo `.json`.
   **Guárdalo bien y no lo subas a GitHub ni lo mandes por chat.**
5. Copia el correo de la cuenta de servicio (termina en `iam.gserviceaccount.com`).

## Parte B · El Google Sheet
1. Crea un Google Sheet vacío llamado `Control de Vacaciones - Datos`.
2. Botón **Compartir** → pega el correo de la cuenta de servicio → rol **Editor**.
3. Copia el ID del Sheet, que es lo que está entre `/d/` y `/edit` en la URL:
   `https://docs.google.com/spreadsheets/d/`**`1AbC...xyz`**`/edit`

No necesitas crear pestañas: la app crea `equipos`, `empleados`, `vacaciones` y
`feriados` sola.

## Parte C · Probar en tu PC
En Git Bash, dentro de la carpeta de la app y con el entorno activo
(`source .venv/Scripts/activate`):
```bash
python -m pip install -r requirements.txt
cp secrets.toml.example .streamlit/secrets.toml
code .streamlit/secrets.toml
```
Llena `spreadsheet_id` y copia cada campo del `.json` en `[gcp_service_account]`.
`private_key` va **en una sola línea**, con los `\n` tal cual vienen en el JSON.

**Subir los datos que ya tienes** (opcional, una vez):
```bash
python subir_csv_a_sheets.py
```

**Arrancar la app:**
```bash
python -m streamlit run app.py
```
En el menú lateral, abajo, debe decir **Datos: Google Sheets (compartido)**.
Registra un periodo de prueba y confirma que aparece en el Sheet.

## Parte D · Subir el código a tu repositorio PRIVADO de GitHub
1. En github.com → **New repository** → nombre `control-vacaciones` → **Private**
   → sin README → Create.
2. En Git Bash, en la carpeta de la app:
```bash
git status                       # tu carpeta ya es repo (aparece "main")
git rm -r --cached data .streamlit/secrets.toml 2>/dev/null   # por si se subieron antes
git add .
git status                       # REVISA: NO deben aparecer data/ ni secrets.toml ni el .json
git commit -m "App de vacaciones con Google Sheets"
git remote -v                    # si no sale nada, agrega el remoto:
git remote add origin https://github.com/TU_USUARIO/control-vacaciones.git
git push -u origin main
```
El `.gitignore` incluido bloquea `data/`, `.streamlit/secrets.toml` y los `.json`.

## Parte E · Publicar en Streamlit Cloud
1. Entra a https://share.streamlit.io con tu cuenta de GitHub y autoriza el acceso
   a repositorios privados.
2. **Create app** → la opción de desplegar desde un repositorio de GitHub
   (aunque diga "public app", la visibilidad se ajusta en la Parte F). Elige:
   - Repository: `TU_USUARIO/control-vacaciones`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: el nombre que quieras
3. **Advanced settings**:
   - Python version: 3.12.
   - **Secrets**: pega el contenido completo de tu `.streamlit/secrets.toml`.
4. **Deploy**. La primera vez tarda 2 a 5 minutos.

## Parte F · Dar acceso al equipo
En la app publicada → **Share** → deja la app como **privada** (que no la vea
"cualquiera con el link") y agrega los correos del equipo. Cada persona entra
con ese correo, sea cuenta de Google o de GitHub.

> Revisa en la ventana Share cuántas apps privadas permite tu plan gratuito. Si
> no te deja hacerla privada, no la publiques: los datos quedarían a la vista de
> cualquiera que tenga el link.

---

## Cómo funciona y qué tener en cuenta
- **Actualización:** la app reutiliza cada lectura del Sheet hasta 30 s (para no
  agotar la cuota de Google). Lo que guardas tú lo ves al instante; lo que guarda
  otra persona, en máximo 30 s (o al recargar después de ese tiempo).
- **Dos personas guardando al mismo tiempo:** cada guardado reescribe la tabla
  completa. Si dos personas guardan en el mismo instante, puede perderse uno de
  los dos cambios. Para un equipo pequeño es raro; si pasa, se ve en el Sheet.
- **Respaldo:** en el Google Sheet, **Archivo → Historial de versiones** te deja
  volver a cualquier momento. Además, en la app, **Datos** sigue permitiendo
  descargar CSV/Excel.
- **Zona peligrosa:** cualquiera con acceso a la app puede usar "Borrar datos".
  Si pasa, se recupera con el historial de versiones del Sheet.
- **App dormida:** si nadie entra por un tiempo, Streamlit Cloud la suspende. Al
  entrar aparece un botón para despertarla (unos segundos). Los datos no se pierden.
- **Actualizar la app:** cambia `app.py` en tu PC, luego
  `git add . && git commit -m "cambio" && git push`. Streamlit Cloud se
  actualiza solo en uno o dos minutos.
- **En tu PC sin `secrets.toml`:** la app sigue usando los CSV de `data/` como antes.

## Problemas frecuentes
| Mensaje en la app | Solución |
|---|---|
| `No se pudo leer en Google Sheets: SpreadsheetNotFound` | El Sheet no está compartido con el correo de la cuenta de servicio, o el ID está mal |
| `... APIError ... has not been used in project` | Falta habilitar Google Sheets API o Drive API (Parte A, paso 2) |
| `... Quota exceeded` | Demasiadas lecturas en un minuto: espera 1 minuto y recarga |
| `... Invalid JWT / private key` | `private_key` mal copiada: debe conservar los `\n` y las comillas |
| Sidebar dice "CSV local" en la nube | Los Secrets no se guardaron: Streamlit Cloud → app → Settings → Secrets |
