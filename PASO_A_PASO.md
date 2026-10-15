# Control de Vacaciones — paso a paso (Windows + Git Bash / VS Code)

## 0. Copiar los archivos
Copia en tu carpeta del proyecto
(`~/Downloads/APP_VACACIONES/APP_VACACIONES/Proeyecci-n-Vacaciones`):

```
app.py               ← reemplaza tu archivo anterior (debe llamarse app.py, NO .txt)
requirements.txt
iniciar_app.sh       ← lanzador para Git Bash
iniciar_app.bat      ← lanzador con doble clic
.streamlit/config.toml
```
Si ya tienes una carpeta `data/` con tus CSV, **no la borres**: ahí están tus datos.

## 1. Abrir la terminal en la carpeta correcta
En Git Bash:
```bash
cd ~/Downloads/APP_VACACIONES/APP_VACACIONES/Proeyecci-n-Vacaciones
ls          # debes ver app.py y requirements.txt
```
En VS Code: **File → Open Folder…** y abre esa carpeta (no la carpeta de arriba).
Luego **Terminal → New Terminal**.

> La app SIEMPRE debe arrancarse desde esta carpeta. Si la arrancas desde otra,
> Streamlit no encuentra `.streamlit/config.toml` ni `data/`.

## 2. Crear el entorno virtual (solo la primera vez)
```bash
python -m venv .venv
```
(si `python` no existe, prueba `py -m venv .venv`)

## 3. Activar el entorno virtual (cada vez que abras una terminal)
Git Bash:
```bash
source .venv/Scripts/activate
```
PowerShell (terminal por defecto de VS Code):
```powershell
.venv\Scripts\Activate.ps1
```
> Si PowerShell dice que los scripts están deshabilitados, ejecuta una vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentar.

Sabrás que está activo porque aparece `(.venv)` al inicio de la línea.

En VS Code, además: `Ctrl+Shift+P` → **Python: Select Interpreter** → elige el
que dice `.venv`.

## 4. Instalar / actualizar dependencias
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit version      # debe decir 1.50 o mayor
```

## 5. Correr la aplicación
```bash
python -m streamlit run app.py
```
o simplemente `./iniciar_app.sh` (Git Bash) o doble clic en `iniciar_app.bat`.

Se abre en http://localhost:8501. Para detenerla: `Ctrl+C` en la terminal.

## 6. La primera vez después de actualizar
Recarga el navegador con **Ctrl+F5**. La app borra sola el tema viejo que
Streamlit guardaba en el navegador (era lo que pintaba naranja) y recarga una vez.
Si aún ves naranja: abre la app en una ventana de incógnito para confirmar, y
revisa que el paso 4 diga versión 1.50 o mayor.

## 7. Checklist de prueba
1. **Dashboard**: abre el selector de equipo → opciones con fondo azul claro, nada naranja.
2. **Personas**: agrega una persona; revisa el selector de país.
3. **Vacaciones**: registra un periodo; abre los desplegables Persona/Tipo/Estado y
   el calendario de fechas → el día elegido es azul marino.
4. **Calendario**: navega meses; Aprobada = verde lima, Tomada = azul, Solicitada = lila.
5. **Feriados México / Colombia**: carga los oficiales y revisa los colores.
6. **Datos → Auditoría de identidad visual**: debe salir sin colores ajenos.

## Problemas frecuentes
| Síntoma | Solución |
|---|---|
| `streamlit: command not found` | No activaste el entorno (paso 3) o usa `python -m streamlit run app.py` |
| `'str' object cannot be interpreted as an integer` | Streamlit viejo → paso 4 |
| `ModuleNotFoundError` | Paso 4 con el entorno activo |
| Colores naranja / beige | Streamlit viejo o arrancaste desde otra carpeta → pasos 1, 4 y 6 |
| `Port 8501 is already in use` | Ya hay otra app abierta: ciérrala o usa `python -m streamlit run app.py --server.port 8502` |
