# Plan de trabajo: llevar la v12 al repo y publicarla en Streamlit Cloud

**Quién hace qué**
- **Dueño (tu compañero):** es dueño del repo, de la cuenta de Google y de Streamlit Cloud. Trabaja en su PC.
- **Apoyo (tú):** acompañas, revisas y ayudas a diagnosticar.

Las cuentas y credenciales (Google Cloud, Sheet, Streamlit Cloud) van a nombre
del dueño: es su app y él debe poder administrarla sin depender de ti.

**Regla de oro:** los cambios entran primero en una **rama nueva**, no en `main`.
Si algo sale mal, `main` queda intacto y se vuelve atrás en segundos.

---

## Fase 0 · Preparación (10 min)
- [ ] El dueño confirma que su repo está al día y sin cambios pendientes:
  ```bash
  cd <carpeta-del-repo>
  git status                # debe decir "nothing to commit, working tree clean"
  git pull
  ```
  Si hay cambios sin guardar: `git add . && git commit -m "Respaldo antes de v12"`.
- [ ] **Respaldo de datos:** copiar la carpeta `data/` a un lugar fuera del repo
  (ej. el Escritorio, `data_respaldo_AAAA-MM-DD`). Son los datos reales del equipo.
- [ ] Anotar el nombre del archivo principal actual de la app (ej. `app.py`,
  `app_v10.py`). Lo necesitarán en las fases 1 y 5.

## Fase 1 · Meter la v12 en una rama (15 min)
```bash
git checkout -b v12-google-sheets
```
- [ ] Extraer el `.zip` **dentro de la carpeta del repo**, reemplazando archivos.
  Incluye `.gitignore` y `.streamlit/` (carpetas o archivos que empiezan con punto):
  verificar que se copiaron.
- [ ] Si el archivo principal anterior tenía otro nombre (ej. `app_v10.py`),
  borrarlo para que solo quede `app.py`: `git rm app_v10.py`.
- [ ] Sacar del control de versiones lo que no debe estar en GitHub (si estaba):
  ```bash
  git rm -r --cached data .streamlit/secrets.toml 2>/dev/null
  ```
- [ ] Revisar qué cambió antes de guardar:
  ```bash
  git status
  git diff --stat
  ```
  **No deben aparecer** `data/`, `secrets.toml` ni archivos `.json`.

## Fase 2 · Probar en local con los CSV (15 min)
Sigue `PASO_A_PASO.md` (pasos 2 a 5): entorno virtual, `pip install -r requirements.txt`
y `python -m streamlit run app.py`.
- [ ] La app abre sin errores y en el menú lateral dice **Datos: CSV local**.
- [ ] Se ven sus datos reales (personas, vacaciones, feriados).
- [ ] No hay naranjas ni beige (checklist del paso 7 de `PASO_A_PASO.md`).
- [ ] Guardar el avance en la rama:
  ```bash
  git add .
  git commit -m "v12: corrección de colores y soporte para Google Sheets"
  git push -u origin v12-google-sheets
  ```
**Si algo falla aquí:** no seguir. Mandar el mensaje de error.

## Fase 3 · Google Cloud y el Sheet (20–30 min, cuenta del dueño)
Seguir `STREAMLIT_CLOUD.md`, Partes A y B.
- [ ] Proyecto creado y Google Sheets API y Google Drive API habilitadas.
- [ ] Cuenta de servicio creada y clave `.json` descargada. **Guardarla fuera del
  repo** (ej. Documentos). Nunca enviarla por chat ni por correo.
- [ ] Google Sheet creado y compartido como **Editor** con el correo de la cuenta de servicio.
- [ ] ID del Sheet anotado.

## Fase 4 · Probar en local con Google Sheets (15 min)
`STREAMLIT_CLOUD.md`, Parte C.
- [ ] Crear y llenar `.streamlit/secrets.toml` (a partir de `secrets.toml.example`).
- [ ] `git status` **no** muestra `secrets.toml` (lo bloquea el `.gitignore`).
- [ ] `python subir_csv_a_sheets.py` → responde `si` → aparecen las 4 pestañas en el Sheet.
- [ ] Arrancar la app: el menú lateral dice **Datos: Google Sheets (compartido)** y se
  ven los mismos datos que en la Fase 2.
- [ ] Prueba de escritura: registrar un periodo de prueba, verlo en el Sheet y luego borrarlo.

## Fase 5 · Pasar a `main` (5 min)
Solo si las fases 2 y 4 salieron bien:
```bash
git checkout main
git merge v12-google-sheets
git push
```
(O abrir un Pull Request en GitHub de `v12-google-sheets` a `main` y aprobarlo.)

## Fase 6 · Publicar en Streamlit Cloud (15 min)
`STREAMLIT_CLOUD.md`, Partes E y F.
- [ ] App creada desde el repo, rama `main`, archivo `app.py`.
- [ ] Secrets pegados (contenido de `.streamlit/secrets.toml`).
- [ ] La app publicada dice **Datos: Google Sheets (compartido)**.
- [ ] App **privada** e invitación enviada a 1 o 2 personas para probar.

## Fase 7 · Prueba con el equipo y salida (1–2 días)
- [ ] Dos personas abren la app al mismo tiempo: una registra un periodo y la otra
  lo ve (puede tardar hasta 30 s).
- [ ] Probar en Chrome y Edge, incluida una ventana de incógnito.
- [ ] Si todo está bien: invitar al resto del equipo y avisar que la versión
  local con CSV ya no se usa para registrar (para no tener dos fuentes de datos).

---

## Si algo sale mal: cómo volver atrás
| Situación | Qué hacer |
|---|---|
| Falla en la Fase 1 o 2 | `git checkout main`: todo vuelve a como estaba. Borrar la rama: `git branch -D v12-google-sheets` |
| Ya se hizo merge a `main` y hay un problema | `git revert -m 1 HEAD` y `git push` (deshace el merge sin borrar historia) |
| Se borraron datos del Sheet | Google Sheet → **Archivo → Historial de versiones** |
| Se perdieron los CSV | Copiar de vuelta `data_respaldo_...` de la Fase 0 |
| Se subió por error `secrets.toml` o el `.json` a GitHub | Avisar al instante: en Google Cloud **borrar esa clave** y crear una nueva. Sacar el archivo del repo no basta, porque queda en el historial |
