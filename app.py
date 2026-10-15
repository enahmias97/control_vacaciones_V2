# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
 WPP MEDIA · CONTROL DE VACACIONES MULTI-EQUIPO — v11
 México / Colombia · People Operations LATAM
 Autor: Fernando Nahmias
═══════════════════════════════════════════════════════════════════════════════
 FUENTE ÚNICA DE COLOR — Brand Guidelines 2025 v1.0
   Primaria   : WPP Navy #000050 · White #FFFFFF · Lime Green #B0F467
                WPP Pantone 629 #93DFE3
   Secundaria : Cornflower Blue #5465FF · Periwinkle #788BFF · Teal #00DBEE
   EXCLUIDO por indicación del equipo de marca: Yellow
 Todo tono intermedio es rgba() de estos mismos hex (los neutros del brand
 book son White y WPP Navy, por eso no existe ningún gris propio).
 La función auditar_colores() verifica esta regla sobre el propio archivo.
═══════════════════════════════════════════════════════════════════════════════
"""

import base64
import calendar
import io
import os
import re
from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
import streamlit.components.v1 as components

# ═══════════════════════════════════════════════════════════════════════════
# 1 · PALETA CORPORATIVA — ÚNICA FUENTE DE VERDAD
# ═══════════════════════════════════════════════════════════════════════════
NAVY       = "#000050"
WHITE      = "#FFFFFF"
LIME       = "#B0F467"
P629       = "#93DFE3"
CORNFLOWER = "#5465FF"
PERIWINKLE = "#788BFF"
TEAL       = "#00DBEE"

PALETA_OFICIAL = [NAVY, WHITE, LIME, P629, CORNFLOWER, PERIWINKLE, TEAL]
HEX_PERMITIDOS = {c.upper().lstrip("#") for c in PALETA_OFICIAL}
# Tintes claros de la paleta en hex (Streamlit no acepta rgba en el tema)
HEX_PERMITIDOS |= {"EEF0FF", "E6FBFD", "F1F3FF", "F2F2F6"}
NOMBRE_COLOR = {NAVY: "WPP Navy", WHITE: "White", LIME: "Lime Green",
                P629: "WPP Pantone 629", CORNFLOWER: "Cornflower Blue",
                PERIWINKLE: "Periwinkle", TEAL: "Teal"}

def rgba(hex_color: str, alpha: float) -> str:
    """Tinte del MISMO color de marca. No puede introducir tonos nuevos."""
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{alpha})"

# --- Tintes derivados (todos rgba de la paleta) ---
MUTED      = rgba(NAVY, .58)
FAINT      = rgba(NAVY, .30)
GHOST      = rgba(NAVY, .13)
LINE       = rgba(NAVY, .14)
LINE_SOFT  = rgba(NAVY, .07)
SURF       = rgba(NAVY, .045)
SURF_2     = rgba(NAVY, .085)
# Lime a baja opacidad sobre blanco se percibe crema/beige. Por eso los fondos
# "verdes" usan Lime con opacidad alta (se ve verde) y los lavados suaves usan
# Teal / Pantone 629 (azul-verde frío).
LIME_BG    = rgba(LIME, .55)
LIME_BG_LT = rgba(TEAL, .10)
P629_BG    = rgba(P629, .30)
P629_BG_LT = rgba(P629, .15)
CORN_BG    = rgba(CORNFLOWER, .13)
PERI_BG    = rgba(PERIWINKLE, .16)
TEAL_BG    = rgba(TEAL, .14)

FONT = "'WPP',system-ui,-apple-system,'Segoe UI',sans-serif"

ASSETS_DIR = "assets"
FONT_DIRS = [os.path.join("static", "fonts"), os.path.join(ASSETS_DIR, "fonts"), "fonts"]

CONFIG_TOML = f'''# WPP Media — Brand Guidelines 2025 v1.0
[theme]
base = "light"
primaryColor = "{NAVY}"
backgroundColor = "{WHITE}"
secondaryBackgroundColor = "{WHITE}"
textColor = "{NAVY}"
linkColor = "{CORNFLOWER}"
borderColor = "{P629}"
font = "WPP"
headingFont = "WPP"
codeFont = "WPP"
[theme.sidebar]
backgroundColor = "{WHITE}"
secondaryBackgroundColor = "{WHITE}"
textColor = "{NAVY}"
primaryColor = "{NAVY}"
borderColor = "{P629}"

[[theme.fontFaces]]
family = "WPP"
url = "app/static/fonts/WPP-Regular.woff2"
weight = 400
style = "normal"

[[theme.fontFaces]]
family = "WPP"
url = "app/static/fonts/WPP-Medium.woff2"
weight = 500
style = "normal"

[[theme.fontFaces]]
family = "WPP"
url = "app/static/fonts/WPP-Bold.woff2"
weight = 700
style = "normal"

[server]
enableStaticServing = true
runOnSave = true
'''

# ═══════════════════════════════════════════════════════════════════════════
# 2 · LOGO — se usa el archivo original, sin recortes ni reescalados
# ═══════════════════════════════════════════════════════════════════════════
def find_logo():
    exactos = [
        os.path.join(ASSETS_DIR, "WPP Media_Wordmark_Navy_RGB.png"),
        "WPP Media_Wordmark_Navy_RGB.png",
        os.path.join("static", "WPP Media_Wordmark_Navy_RGB.png"),
        os.path.join(ASSETS_DIR, "wpp_media_logo.png"),
    ]
    for p in exactos:
        if os.path.exists(p):
            return p
    for carpeta in (ASSETS_DIR, ".", "static", "img", "images", "logo"):
        if not os.path.isdir(carpeta):
            continue
        try:
            archivos = sorted(os.listdir(carpeta))
        except OSError:
            continue
        for f in archivos:
            low = f.lower()
            if low.endswith((".png", ".jpg", ".jpeg", ".webp")) and "wpp" in low and \
               any(t in low for t in ("wordmark", "media", "logo", "navy")):
                return os.path.join(carpeta, f)
    return None

LOGO = find_logo()

@st.cache_data(show_spinner=False)
def logo_uri(path):
    if not path:
        return None
    try:
        mime = "image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/png"
        return f"data:{mime};base64,{base64.b64encode(open(path,'rb').read()).decode()}"
    except Exception:
        return None

LOGO_URI = logo_uri(LOGO)

# ═══════════════════════════════════════════════════════════════════════════
# 1B · TEMA CORPORATIVO FORZADO DESDE EL CÓDIGO
#   Sin un config.toml correcto, Streamlit usa su tema por defecto (naranja /
#   rojo / crema) en radios, chips, toggles, selects y barras. Aquí se fija el
#   tema en tiempo de ejecución, así funciona aunque config.toml no exista.
# ═══════════════════════════════════════════════════════════════════════════
TEMA_RUNTIME = {
    "base": "light",
    "primaryColor": NAVY, "backgroundColor": WHITE,
    "secondaryBackgroundColor": WHITE, "textColor": NAVY,
    "linkColor": CORNFLOWER, "borderColor": P629,
    # Paleta semántica de Streamlit → solo colores de marca (adiós naranja/café)
    "redColor": CORNFLOWER, "orangeColor": TEAL, "yellowColor": LIME,
    "blueColor": CORNFLOWER, "greenColor": LIME, "violetColor": PERIWINKLE,
    "grayColor": NAVY,
    "redBackgroundColor": "#EEF0FF", "orangeBackgroundColor": "#E6FBFD",
    "yellowBackgroundColor": "#E6FBFD", "blueBackgroundColor": "#EEF0FF",
    "greenBackgroundColor": "#E6FBFD", "violetBackgroundColor": "#F1F3FF",
    "grayBackgroundColor": "#F2F2F6",
    "redTextColor": NAVY, "orangeTextColor": NAVY, "yellowTextColor": NAVY,
    "blueTextColor": NAVY, "greenTextColor": NAVY, "violetTextColor": NAVY,
    "grayTextColor": NAVY,
    "dataframeHeaderBackgroundColor": "#F2F2F6",
    "chartCategoricalColors": [NAVY, CORNFLOWER, TEAL, LIME, PERIWINKLE, P629],
}
TEMA_SIDEBAR = {"backgroundColor": WHITE, "secondaryBackgroundColor": WHITE,
                "textColor": NAVY, "primaryColor": NAVY, "borderColor": P629}

def aplicar_tema_runtime():
    try:
        from streamlit import config as _stcfg
    except Exception:
        return
    cambio = False
    for sec, opciones in (("theme", TEMA_RUNTIME), ("theme.sidebar", TEMA_SIDEBAR)):
        for k, v in opciones.items():
            clave = f"{sec}.{k}"
            try:
                if _stcfg.get_option(clave) != v:
                    _stcfg.set_option(clave, v)
                    cambio = True
            except Exception:
                pass                       # opción no disponible en esta versión
    # El tema viaja al navegador al inicio de cada ejecución: si se acaba de
    # cambiar, se relanza UNA vez para que se pinte ya con los colores de marca.
    if cambio and not st.session_state.get("_tema_ok"):
        st.session_state["_tema_ok"] = True
        st.rerun()

aplicar_tema_runtime()

st.set_page_config(page_title="Control de Vacaciones · WPP Media",
                   page_icon=LOGO if LOGO else None,
                   layout="wide", initial_sidebar_state="expanded")

# ═══════════════════════════════════════════════════════════════════════════
# 1C · TEMA GUARDADO EN EL NAVEGADOR
#   Streamlit recuerda en localStorage el último tema elegido ("Light", "Dark",
#   "Use system setting"). Si quedó guardado uno de esos, el navegador IGNORA el
#   tema corporativo y pinta el rojo-naranja #FF4B4B y los fondos crema por
#   defecto. Como el menú de Streamlit está oculto, no se puede cambiar a mano:
#   se borra aquí y se recarga la página una sola vez.
# ═══════════════════════════════════════════════════════════════════════════
def limpiar_tema_navegador():
    if st.session_state.get("_tema_nav_ok"):
        return
    st.session_state["_tema_nav_ok"] = True
    components.html("""<script>
    try {
      // Formato viejo (Streamlit < 1.4x): {"name":"Light",...}. El formato nuevo
      // ("System"/"Light"/"Dark") ya respeta el tema corporativo: no se toca.
      const ls = window.parent.localStorage, ss = window.parent.sessionStorage;
      let recargar = false;
      for (let i = ls.length - 1; i >= 0; i--) {
        const k = ls.key(i), v = (k && ls.getItem(k)) || "";
        if (k && k.indexOf("stActiveTheme") === 0 && v.indexOf("{") === 0 &&
            v.indexOf("Custom Theme") === -1) {
          ls.removeItem(k); recargar = true;
        }
      }
      // Recarga como máximo una vez por pestaña (nunca en bucle)
      if (recargar && !ss.getItem("wpp_tema_recargado")) {
        ss.setItem("wpp_tema_recargado", "1");
        window.parent.location.reload();
      }
    } catch (e) {}
    </script>""", height=0)

limpiar_tema_navegador()


# ═══════════════════════════════════════════════════════════════════════════
# 3 · PLANTILLA PLOTLY CORPORATIVA (sustituye a plotly_white)
# ═══════════════════════════════════════════════════════════════════════════
PALETA_SERIES = [NAVY, CORNFLOWER, TEAL, LIME, PERIWINKLE, P629]
ESCALA_CONTINUA = [P629, TEAL, CORNFLOWER, NAVY]

pio.templates["wpp"] = go.layout.Template(
    layout=dict(
        colorway=PALETA_SERIES,
        colorscale=dict(sequential=ESCALA_CONTINUA,
                        sequentialminus=ESCALA_CONTINUA,
                        diverging=[NAVY, P629, LIME]),
        piecolorway=PALETA_SERIES,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=NAVY, size=12),
        title=dict(font=dict(family=FONT, color=NAVY)),
        legend=dict(font=dict(family=FONT, color=NAVY, size=11),
                    bgcolor="rgba(0,0,0,0)", bordercolor=LINE),
        hoverlabel=dict(font=dict(family=FONT, color=NAVY), bgcolor=WHITE,
                        bordercolor=rgba(NAVY, .25)),
        xaxis=dict(gridcolor=LINE_SOFT, linecolor=LINE, zerolinecolor=LINE,
                   tickfont=dict(color=NAVY), title=dict(font=dict(color=NAVY))),
        yaxis=dict(gridcolor=LINE_SOFT, linecolor=LINE, zerolinecolor=LINE,
                   tickfont=dict(color=NAVY), title=dict(font=dict(color=NAVY))),
        coloraxis=dict(colorbar=dict(outlinecolor=LINE, tickfont=dict(color=NAVY))),
        separators=",.",
    )
)
pio.templates.default = "wpp"
px.defaults.template = "wpp"
px.defaults.color_discrete_sequence = PALETA_SERIES
px.defaults.color_continuous_scale = ESCALA_CONTINUA

# ═══════════════════════════════════════════════════════════════════════════
# 4 · CONSTANTES DE NEGOCIO
# ═══════════════════════════════════════════════════════════════════════════
DATA_DIR = "data"
F_EQUIPOS = os.path.join(DATA_DIR, "equipos.csv")
F_EMPLEADOS = os.path.join(DATA_DIR, "empleados.csv")
F_VACACIONES = os.path.join(DATA_DIR, "vacaciones.csv")
F_FERIADOS = os.path.join(DATA_DIR, "feriados.csv")

PAISES = ["México", "Colombia"]
COD_PAIS = {"México": "MX", "Colombia": "CO"}
ESTADOS = ["Solicitada", "Aprobada", "Tomada", "Rechazada"]
ESTADOS_CUENTAN = ["Aprobada", "Tomada"]
TIPOS = ["Vacaciones", "Permiso", "Incapacidad", "Home office", "Otro"]

ESTADO_STYLE = {
    "Solicitada": (PERI_BG, NAVY, PERIWINKLE),
    "Aprobada":   (LIME_BG, NAVY, LIME),
    "Tomada":     (CORN_BG, NAVY, CORNFLOWER),
    "Rechazada":  (SURF_2, MUTED, rgba(NAVY, .35)),
}
COLOR_ESTADO = {k: v[2] for k, v in ESTADO_STYLE.items()}
COLOR_CONCEPTO = {"Tomados": CORNFLOWER, "Proyectados": LIME,
                  "En solicitud": PERIWINKLE, "Saldo": P629}

FERIADO_COLOR = {"México": LIME, "Colombia": TEAL}
FERIADO_BG = {"México": rgba(LIME, .60), "Colombia": rgba(P629, .35)}
COLOR_PAIS = {"México": LIME, "Colombia": TEAL}

PALETA_PERSONAS = [NAVY, CORNFLOWER, TEAL, PERIWINKLE, LIME, P629]

MESES_ES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

TODOS = "__ALL__"

# ═══════════════════════════════════════════════════════════════════════════
# 5 · TIPOGRAFÍA Y AUDITORÍAS
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def font_faces():
    """Incrusta las 3 variantes WPP. No se usa ninguna otra tipografía."""
    variantes = [("WPP-Regular", 400), ("WPP-Medium", 500), ("WPP-Bold", 700)]
    exts = {".woff2": "woff2", ".woff": "woff", ".ttf": "truetype", ".otf": "opentype"}
    css, hallados = [], []
    for base, peso in variantes:
        listo = False
        for carpeta in FONT_DIRS:
            if listo or not os.path.isdir(carpeta):
                continue
            for ext, fmt in exts.items():
                ruta = os.path.join(carpeta, base + ext)
                if os.path.exists(ruta):
                    try:
                        b64 = base64.b64encode(open(ruta, "rb").read()).decode()
                    except Exception:
                        continue
                    css.append(f"@font-face{{font-family:'WPP';"
                               f"src:url(data:font/{fmt};base64,{b64}) format('{fmt}');"
                               f"font-weight:{peso};font-style:normal;font-display:block;}}")
                    hallados.append(base + ext)
                    listo = True
                    break
    return "\n".join(css), hallados

@st.cache_data(show_spinner=False)
def leer_config():
    ruta = os.path.join(".streamlit", "config.toml")
    if not os.path.exists(ruta):
        return {"existe": False, "primary": False, "font": False, "fondo": False,
                "secundario": False, "ruta": ruta}
    try:
        txt = open(ruta, encoding="utf-8", errors="ignore").read()
    except Exception:
        return {"existe": True, "primary": False, "font": False, "fondo": False,
                "secundario": False, "ruta": ruta}
    p = txt.lower().replace(" ", "").replace("'", '"')
    hexes = {h.upper() for h in re.findall(r"#([0-9a-fA-F]{6})", txt)}
    return {"existe": True,
            "primary": f'primarycolor="{NAVY.lower()}"' in p,
            "font": 'font="wpp"' in p,
            "fondo": f'backgroundcolor="{WHITE.lower()}"' in p,
            "secundario": hexes.issubset(HEX_PERMITIDOS),
            "ruta": ruta}

CFG = leer_config()
if not (CFG["existe"] and CFG["primary"] and CFG["font"] and CFG["secundario"]):
    try:
        os.makedirs(".streamlit", exist_ok=True)
        with open(os.path.join(".streamlit", "config.toml"), "w", encoding="utf-8") as _fh:
            _fh.write(CONFIG_TOML)
        leer_config.clear()
        CFG = leer_config()
    except Exception:
        pass

@st.cache_data(show_spinner=False)
def auditar_colores():
    """Escanea este mismo archivo buscando colores fuera de la paleta."""
    try:
        src = open(__file__, encoding="utf-8", errors="ignore").read()
    except Exception:
        return None
    intrusos, nombres = {}, {}
    for h in re.findall(r"#([0-9a-fA-F]{3,8})\b", src):
        hu = h.upper()
        if len(hu) == 6 and hu not in HEX_PERMITIDOS:
            intrusos[hu] = intrusos.get(hu, 0) + 1
        elif len(hu) in (3, 4, 8):
            intrusos[hu] = intrusos.get(hu, 0) + 1
    prohibidos = ("beige", "wheat", "tan", "brown", "chocolate", "orange", "coral",
                  "peru", "sienna", "khaki", "gold", "yellow", "olive", "salmon",
                  "crimson", "tomato", "firebrick", "red", "green", "lightgray",
                  "lightgrey", "gray", "grey", "silver", "linen", "ivory", "cornsilk")
    low = src.lower()
    for n in prohibidos:
        for pat in (f'"{n}"', f"'{n}'", f":{n};", f": {n};"):
            if pat in low:
                nombres[n] = nombres.get(n, 0) + low.count(pat)
    hsl = len(re.findall(r"\bhsl\(", low))
    rgb_crudo = len(re.findall(r"\brgb\(", low))
    return {"hex": intrusos, "nombres": nombres, "hsl": hsl, "rgb": rgb_crudo,
            "rgba_marca": len(re.findall(r"rgba\(", low))}

# ═══════════════════════════════════════════════════════════════════════════
# 6 · CSS GLOBAL — variables centralizadas + neutralización de defaults
# ═══════════════════════════════════════════════════════════════════════════
def inject_css():
    faces, _ = font_faces()



    st.markdown(f"""
    <style>
    {faces}

    /* ╔════════════════════════════════════════════════════════════════╗
       ║ VARIABLES CENTRALIZADAS — único lugar donde viven los colores  ║
       ╚════════════════════════════════════════════════════════════════╝ */
    :root, .stApp {{
        --wpp-navy:{NAVY};
        --wpp-white:{WHITE};
        --wpp-lime:{LIME};
        --wpp-p629:{P629};
        --wpp-cornflower:{CORNFLOWER};
        --wpp-periwinkle:{PERIWINKLE};
        --wpp-teal:{TEAL};
        --wpp-muted:{MUTED};
        --wpp-faint:{FAINT};
        --wpp-line:{LINE};
        --wpp-line-soft:{LINE_SOFT};
        --wpp-surf:{SURF};
        --wpp-font:{FONT};

        /* Sobrescritura de las variables internas de Streamlit */
        --font:{FONT};
        --font-family:{FONT};
        --primary-color:{NAVY};
        --text-color:{NAVY};
        --background-color:{WHITE};
        --secondary-background-color:{WHITE};
        --border-color:{LINE};
        --link-color:{CORNFLOWER};

        /* glide-data-grid: motor en canvas de st.dataframe / st.data_editor */
        --gdg-font-family:{FONT};
        --gdg-accent-color:{NAVY};
        --gdg-accent-fg:{WHITE};
        --gdg-accent-light:{P629_BG_LT};
        --gdg-text-dark:{NAVY};
        --gdg-text-medium:{MUTED};
        --gdg-text-light:{FAINT};
        --gdg-text-header:{MUTED};
        --gdg-text-header-selected:{NAVY};
        --gdg-bg-cell:{WHITE};
        --gdg-bg-cell-medium:{SURF};
        --gdg-bg-header:{SURF};
        --gdg-bg-header-has-focus:{SURF_2};
        --gdg-bg-header-hovered:{P629_BG_LT};
        --gdg-bg-bubble:{SURF};
        --gdg-bg-bubble-selected:{P629_BG};
        --gdg-border-color:{LINE_SOFT};
        --gdg-horizontal-border-color:{LINE_SOFT};
        --gdg-drilldown-border:{LINE};
        --gdg-link-color:{CORNFLOWER};
        --gdg-cell-horizontal-padding:9px;
    }}

    /* ---------- TIPOGRAFÍA: solo WPP. Iconos Material excluidos ---------- */
    html, body, .stApp,
    h1, h2, h3, h4, h5, h6, p, a, li, label, small, strong, b, em,
    table, th, td, caption, code, kbd, pre, samp,
    input, textarea, select, optgroup, button,
    div:not([class*="material"]):not([class*="Material"]),
    span:not([data-testid="stIconMaterial"]):not([class*="material"]):not([class*="Material"]) {{
        font-family:var(--wpp-font) !important;
    }}
    span[data-testid="stIconMaterial"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpandSidebarButton"] span[data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] span[data-testid="stIconMaterial"],
    span.material-symbols-rounded, span.material-symbols-outlined,
    span.material-icons, i.material-icons,
    [class*="material-symbols"], [class*="material-icons"] {{
        font-family:'Material Symbols Rounded','Material Symbols Outlined',
                    'Material Icons' !important;
        font-feature-settings:'liga' 1 !important;
        -webkit-font-feature-settings:'liga' 1 !important;
        font-variation-settings:normal !important;
        letter-spacing:normal !important; text-transform:none !important;
        white-space:nowrap !important; overflow:visible !important;
    }}
    .js-plotly-plot text, .js-plotly-plot tspan,
    .js-plotly-plot .legendtext, .js-plotly-plot .gtitle {{
        font-family:var(--wpp-font) !important;
    }}

    /* ---------- LIENZO ---------- */
    .stApp {{
        background:
          radial-gradient(1200px 520px at -6% -12%, {P629_BG_LT} 0%, {rgba(P629,0)} 60%),
          radial-gradient(900px 430px at 104% -6%, {rgba(CORNFLOWER,.08)} 0%, {rgba(CORNFLOWER,0)} 56%),
          var(--wpp-white) !important;
        color:var(--wpp-navy);
    }}
    .block-container {{ padding-top:.9rem; padding-bottom:3rem; max-width:1560px; }}
    header[data-testid="stHeader"] {{ background:transparent !important;
        box-shadow:none !important; }}
    /* Se oculta solo el lado derecho del header (menú, deploy, estado).
       stToolbar NO se oculta: contiene el botón nativo para reabrir el menú. */
    [data-testid="stToolbarActions"], [data-testid="stMainMenu"],
    [data-testid="stAppDeployButton"], [data-testid="stStatusWidget"], #MainMenu,
    footer, [data-testid="stDecoration"] {{ display:none !important; }}
    [data-testid="stToolbar"] {{ background:transparent !important; }}
    [data-testid="stElementContainer"]:has(> iframe[height="0"]),
    .element-container:has(> iframe[height="0"]),
    [data-testid="stCustomComponentV1"][height="0"] {{ display:none !important; }}
    a, a:visited {{ color:var(--wpp-cornflower) !important; }}
    ::selection {{ background:{rgba(TEAL,.30)}; color:var(--wpp-navy); }}
    *::-webkit-scrollbar {{ width:10px; height:10px; }}
    *::-webkit-scrollbar-track {{ background:var(--wpp-surf); }}
    *::-webkit-scrollbar-thumb {{ background:{rgba(NAVY,.28)}; border-radius:6px; }}
    *::-webkit-scrollbar-thumb:hover {{ background:{rgba(NAVY,.45)}; }}

    /* ╔════════════════════════════════════════════════════════════════╗
       ║ BARRA LATERAL + CONTROLES DE VISIBILIDAD                       ║
       ╚════════════════════════════════════════════════════════════════╝ */
    section[data-testid="stSidebar"] {{
        background:var(--wpp-white) !important;
        border-right:1px solid var(--wpp-line);
        transition:width .18s ease, min-width .18s ease;
    }}
    section[data-testid="stSidebar"] > div {{ padding-top:1.0rem; }}
    section[data-testid="stSidebar"] hr {{ border-color:var(--wpp-line) !important; }}
    section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
        padding:7px 12px; border-radius:9px; font-weight:500;
        color:var(--wpp-navy); width:100%; transition:background .14s ease; }}
    section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        background:var(--wpp-surf); }}
    /* Botón «Ocultar» (dentro del menú): siempre visible, no solo al pasar el mouse */
    [data-testid="stSidebarCollapseButton"] {{
        display:inline-flex !important; visibility:visible !important; opacity:1 !important; }}
    [data-testid="stSidebarCollapseButton"] button {{
        background:var(--wpp-white) !important; border:1px solid var(--wpp-line) !important;
        border-radius:9px !important; }}
    [data-testid="stSidebarCollapseButton"] button:hover {{
        background:var(--wpp-navy) !important; border-color:var(--wpp-navy) !important; }}
    /* Botón «Menú» (aparece arriba a la izquierda cuando el panel está oculto) */
    [data-testid="stExpandSidebarButton"] {{
        background:var(--wpp-navy) !important; border:1px solid var(--wpp-navy) !important;
        border-radius:30px !important; padding:4px 14px 4px 8px !important;
        box-shadow:0 6px 16px {rgba(NAVY,.25)} !important; gap:4px; }}
    [data-testid="stExpandSidebarButton"]::after {{
        content:"Menú"; color:var(--wpp-white); font-weight:700; font-size:.82rem;
        font-family:var(--wpp-font); }}
    [data-testid="stExpandSidebarButton"]:hover {{ background:{rgba(NAVY,.85)} !important; }}
    [data-testid="stSidebarCollapseButton"] span[data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] svg {{ color:var(--wpp-navy) !important;
        fill:var(--wpp-navy) !important; }}
    [data-testid="stSidebarCollapseButton"] button:hover span[data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] button:hover svg,
    [data-testid="stExpandSidebarButton"] span[data-testid="stIconMaterial"],
    [data-testid="stExpandSidebarButton"] svg {{ color:var(--wpp-lime) !important;
        fill:var(--wpp-lime) !important; }}

    /* ╔════════════════════════════════════════════════════════════════╗
       ║ NEUTRALIZACIÓN DE COLORES POR DEFECTO (crema / naranja / etc.) ║
       ╚════════════════════════════════════════════════════════════════╝ */
    [data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"],
    [data-baseweb="select"] > div, [data-baseweb="input"] > div,
    .stTextInput div[data-baseweb="input"], .stNumberInput div[data-baseweb="input"],
    .stDateInput div[data-baseweb="input"], .stTextArea div[data-baseweb="textarea"],
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div,
    [data-testid="stFileUploaderDropzone"], [data-testid="stNumberInputContainer"] {{
        background:var(--wpp-white) !important; background-color:var(--wpp-white) !important;
        border-color:var(--wpp-line) !important; color:var(--wpp-navy) !important;
        border-radius:9px !important; }}
    input, textarea {{ background:transparent !important; color:var(--wpp-navy) !important; }}
    input::placeholder, textarea::placeholder {{ color:var(--wpp-faint) !important; }}
    [data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within,
    [data-baseweb="textarea"]:focus-within {{
        border-color:var(--wpp-navy) !important;
        box-shadow:0 0 0 2px {rgba(CORNFLOWER,.28)} !important; }}
    [data-baseweb="select"] svg, [data-baseweb="input"] svg {{
        fill:var(--wpp-navy) !important; color:var(--wpp-navy) !important; }}
    /* Chips de multiselect */
    [data-baseweb="tag"] {{ background:var(--wpp-navy) !important;
        border:none !important; border-radius:30px !important; }}
    [data-baseweb="tag"] span, [data-baseweb="tag"] div,
    [data-baseweb="tag"] svg, [data-baseweb="tag"] path {{
        color:var(--wpp-white) !important; fill:var(--wpp-white) !important; }}
    [data-baseweb="tag"]:hover {{ background:{rgba(NAVY,.82)} !important; }}
    /* Menús desplegables */
    [data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"],
    [data-baseweb="popover"] > div {{
        background:var(--wpp-white) !important;
        border:1px solid var(--wpp-line) !important; }}
    [role="option"] {{ color:var(--wpp-navy) !important; }}
    [role="option"][aria-selected="true"], [role="option"]:hover {{
        background:{P629_BG_LT} !important; color:var(--wpp-navy) !important; }}
    /* Calendario del date_input */
    [data-baseweb="calendar"] {{ background:var(--wpp-white) !important; }}
    [data-baseweb="calendar"] [aria-selected="true"],
    [data-baseweb="calendar"] [aria-pressed="true"] {{
        background:var(--wpp-navy) !important; color:var(--wpp-white) !important; }}
    [data-baseweb="calendar"] button:hover {{ background:{P629_BG_LT} !important; }}
    /* Barra de progreso */
    [data-testid="stProgress"] > div > div {{ background:{SURF_2} !important; }}
    [data-testid="stProgress"] div[role="progressbar"] > div,
    [data-testid="stProgress"] > div > div > div > div {{
        background-color:var(--wpp-navy) !important;
        background-image:linear-gradient(90deg,{NAVY},{CORNFLOWER} 62%,{LIME}) !important; }}
    /* Radio · checkbox · toggle · slider */
    [data-testid="stRadio"] [aria-checked="true"] > div:first-child,
    [data-baseweb="radio"] [aria-checked="true"] > div:first-child {{
        background-color:var(--wpp-navy) !important;
        border-color:var(--wpp-navy) !important; }}
    [data-baseweb="checkbox"] [aria-checked="true"],
    [data-baseweb="checkbox"] [data-checked="true"] {{
        background-color:var(--wpp-navy) !important;
        border-color:var(--wpp-navy) !important; }}
    [data-baseweb="checkbox"] svg {{ color:var(--wpp-lime) !important;
        fill:var(--wpp-lime) !important; }}
    [data-baseweb="toggle"], [data-baseweb="toggle"] > div {{
        background-color:var(--wpp-navy) !important; }}
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {{
        background-color:var(--wpp-navy) !important; }}
    [data-testid="stSlider"] [data-testid="stThumbValue"] {{
        color:var(--wpp-navy) !important; }}
    [data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
        background:{SURF_2} !important; }}
    [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {{
        background:var(--wpp-navy) !important; }}
    .stSpinner > div {{ border-top-color:var(--wpp-navy) !important; }}
    /* Alertas nativas → navy (elimina verde, rojo, ámbar y azul genéricos) */
    div[data-testid="stAlert"], div[data-testid="stNotification"],
    div[data-testid="stToast"] {{
        background:var(--wpp-surf) !important; border:1px solid var(--wpp-line) !important;
        border-left:4px solid var(--wpp-navy) !important; border-radius:10px !important; }}
    div[data-testid="stAlert"] *, div[data-testid="stNotification"] *,
    div[data-testid="stToast"] * {{ color:var(--wpp-navy) !important; }}
    div[data-testid="stAlert"] svg, div[data-testid="stNotification"] svg {{
        fill:var(--wpp-navy) !important; color:var(--wpp-navy) !important; }}

    /* ---------- LOGO LOCKUP ---------- */
    .brandbar {{ display:flex; align-items:center; gap:0; margin:0 0 18px; }}
    .brandcard {{ background:var(--wpp-white); border:1px solid var(--wpp-line);
        border-radius:16px; padding:12px 22px; box-shadow:0 3px 14px {rgba(NAVY,.07)};
        display:flex; align-items:center; }}
    .brandcard img {{ height:48px; width:auto; display:block; object-fit:contain; }}
    .brandmeta {{ padding-left:20px; margin-left:20px;
        border-left:1px solid var(--wpp-line); line-height:1.2; }}
    .brandmeta b {{ display:block; font-weight:700; font-size:1.0rem;
        color:var(--wpp-navy); }}
    .brandmeta small {{ display:block; font-weight:500; font-size:.70rem;
        color:var(--wpp-muted); letter-spacing:1.1px; text-transform:uppercase;
        margin-top:4px; }}
    .brandbar .tagmx {{ margin-left:auto; background:var(--wpp-lime);
        color:var(--wpp-navy); font-weight:700; font-size:.70rem; padding:6px 15px;
        border-radius:30px; letter-spacing:.5px; }}
    .sidecard {{ background:var(--wpp-white); border:1px solid var(--wpp-line);
        border-radius:16px; padding:16px 18px; margin:0 0 16px;
        box-shadow:0 3px 14px {rgba(NAVY,.07)}; }}
    .sidecard img {{ width:100%; height:auto; display:block; object-fit:contain; }}
    .sidecard .fb {{ font-weight:700; font-size:1.2rem; color:var(--wpp-navy); }}

    /* ---------- HERO ---------- */
    .hero {{ background:var(--wpp-navy); border-radius:16px; padding:24px 28px;
        margin-bottom:18px; color:var(--wpp-white); position:relative; overflow:hidden;
        box-shadow:0 14px 32px {rgba(NAVY,.20)}; }}
    .hero:before {{ content:""; position:absolute; right:-90px; top:-100px; width:280px;
        height:280px; border-radius:50%; background:{rgba(P629,.10)}; }}
    .hero:after {{ content:""; position:absolute; left:0; top:0; bottom:0; width:5px;
        background:var(--wpp-lime); }}
    .hero h1 {{ margin:0; font-size:1.58rem; font-weight:700; letter-spacing:-.2px;
        color:var(--wpp-white); }}
    .hero h1 em {{ font-style:normal; color:var(--wpp-lime); }}
    .hero p {{ margin:.4rem 0 0; font-size:.90rem; color:{rgba(WHITE,.78)};
        font-weight:400; }}
    .hero .tag {{ display:inline-block; margin-top:12px; background:{rgba(P629,.16)};
        border:1px solid var(--wpp-p629); color:var(--wpp-p629); padding:4px 14px;
        border-radius:30px; font-size:.74rem; font-weight:600; }}

    /* ---------- MÉTRICAS ---------- */
    div[data-testid="stMetric"] {{ background:var(--wpp-white);
        border:1px solid var(--wpp-line); border-radius:13px; padding:14px 16px 13px;
        box-shadow:0 2px 10px {rgba(NAVY,.05)}; border-top:3px solid var(--wpp-lime);
        transition:transform .16s ease, box-shadow .16s ease; }}
    div[data-testid="stMetric"]:hover {{ transform:translateY(-3px);
        box-shadow:0 10px 22px {rgba(NAVY,.11)};
        border-top-color:var(--wpp-cornflower); }}
    div[data-testid="stMetricLabel"] p {{ font-size:.67rem !important; font-weight:600;
        color:var(--wpp-muted); text-transform:uppercase; letter-spacing:.8px; }}
    div[data-testid="stMetricValue"] {{ color:var(--wpp-navy); font-weight:700;
        font-size:1.56rem; }}
    div[data-testid="stMetricDelta"] {{ color:var(--wpp-muted) !important;
        font-size:.72rem; }}
    div[data-testid="stMetricDelta"] svg {{ display:none !important; }}

    /* ---------- BOTONES ---------- */
    .stButton>button, .stDownloadButton>button, .stFormSubmitButton>button,
    [data-testid="stPopover"] button, [data-testid="stFileUploader"] button {{
        border-radius:9px; font-weight:600; border:1px solid var(--wpp-line);
        color:var(--wpp-navy); background:var(--wpp-white); transition:all .16s ease; }}
    .stButton>button:hover, .stDownloadButton>button:hover,
    .stFormSubmitButton>button:hover, [data-testid="stPopover"] button:hover {{
        border-color:var(--wpp-navy); background:var(--wpp-surf);
        transform:translateY(-1px); color:var(--wpp-navy); }}
    .stButton>button:focus-visible, .stDownloadButton>button:focus-visible,
    .stFormSubmitButton>button:focus-visible {{
        outline:none !important; border-color:var(--wpp-navy) !important;
        box-shadow:0 0 0 3px {rgba(CORNFLOWER,.35)} !important; }}
    .stButton>button:active {{ background:{P629_BG_LT} !important; }}
    button[kind="primary"], button[kind="primaryFormSubmit"] {{
        background:var(--wpp-navy) !important; border:1px solid var(--wpp-navy) !important;
        color:var(--wpp-lime) !important; }}
    button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {{
        box-shadow:0 6px 16px {rgba(NAVY,.28)} !important; }}
    button[kind="primary"]:disabled, button[kind="primaryFormSubmit"]:disabled,
    .stButton>button:disabled {{
        background:{rgba(NAVY,.22)} !important; border-color:transparent !important;
        color:var(--wpp-white) !important; opacity:1 !important; }}

    /* ---------- EXPANDERS / TABS / FORMS ---------- */
    div[data-testid="stExpander"] {{ border:1px solid var(--wpp-line);
        border-radius:12px; background:var(--wpp-white);
        box-shadow:0 2px 8px {rgba(NAVY,.04)}; overflow:hidden; }}
    div[data-testid="stExpander"] summary {{ background:var(--wpp-white) !important;
        color:var(--wpp-navy) !important; font-weight:600; }}
    div[data-testid="stExpander"] summary:hover {{ background:var(--wpp-surf) !important; }}
    div[data-testid="stExpander"] summary p {{ margin:0; }}
    div[data-testid="stForm"] {{ border:1px solid var(--wpp-line) !important;
        border-radius:12px !important; background:var(--wpp-white) !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap:4px;
        border-bottom:1px solid var(--wpp-line); flex-wrap:wrap; background:transparent; }}
    .stTabs [data-baseweb="tab"] {{ border-radius:8px 8px 0 0; padding:8px 15px;
        font-weight:600; font-size:.86rem; color:var(--wpp-muted); }}
    .stTabs [data-baseweb="tab"]:hover {{ color:var(--wpp-navy); }}
    .stTabs [aria-selected="true"] {{ background:var(--wpp-surf);
        color:var(--wpp-navy) !important; box-shadow:inset 0 -3px 0 var(--wpp-lime); }}
    .stTabs [data-baseweb="tab-highlight"] {{ background:var(--wpp-lime) !important; }}
    .stTabs [data-baseweb="tab-border"] {{ background:var(--wpp-line) !important; }}

    /* ---------- SECCIONES Y TARJETAS ---------- */
    .sect {{ display:flex; align-items:center; gap:10px; margin:26px 0 12px;
        font-size:1.0rem; font-weight:700; color:var(--wpp-navy); clear:both; }}
    .sect:before {{ content:""; width:4px; height:19px; border-radius:3px; flex:0 0 4px;
        background:linear-gradient(180deg,{LIME},{P629}); }}
    .chtitle {{ font-weight:700; font-size:.92rem; color:var(--wpp-navy);
        margin:16px 0 4px; line-height:1.3; }}
    .chtitle small {{ display:block; font-weight:400; font-size:.76rem;
        color:var(--wpp-muted); margin-top:3px; }}
    .js-plotly-plot .modebar {{ opacity:0; transition:opacity .2s ease; }}
    .js-plotly-plot:hover .modebar {{ opacity:.4; }}
    .js-plotly-plot .modebar-group {{ background:transparent !important; }}
    .js-plotly-plot .modebar-btn svg path {{ fill:{MUTED} !important; }}
    .card {{ background:var(--wpp-white); border:1px solid var(--wpp-line);
        border-radius:12px; padding:14px 16px; margin-bottom:10px;
        box-shadow:0 2px 8px {rgba(NAVY,.04)}; }}
    .row {{ display:flex; align-items:center; gap:12px; padding:11px 14px;
        background:var(--wpp-white); border:1px solid var(--wpp-line);
        border-left:4px solid var(--wpp-navy); border-radius:10px; margin-bottom:8px;
        box-shadow:0 2px 6px {rgba(NAVY,.04)}; }}
    .row .nm {{ font-weight:700; color:var(--wpp-navy); }}
    .row .dt {{ color:var(--wpp-muted); font-size:.82rem; }}
    .pill {{ display:inline-block; padding:2px 10px; border-radius:30px;
        font-size:.69rem; font-weight:600; margin-right:4px; }}
    .nota {{ border-radius:10px; padding:11px 15px; margin:0 0 9px; font-size:.87rem;
        border:1px solid var(--wpp-line); border-left:4px solid var(--wpp-navy);
        color:var(--wpp-navy); background:var(--wpp-surf); line-height:1.5; }}
    .navtitle {{ text-align:center; font-weight:700; font-size:1.12rem;
        color:var(--wpp-navy); line-height:1.15; }}
    .navtitle small {{ display:block; font-weight:500; font-size:.64rem;
        color:var(--wpp-muted); letter-spacing:1.2px; margin-top:3px; }}
    .eqcard {{ background:var(--wpp-white); border:1px solid var(--wpp-line);
        border-radius:12px; padding:13px 15px; box-shadow:0 2px 8px {rgba(NAVY,.04)};
        border-left:5px solid var(--wpp-navy); margin-bottom:9px; }}
    .eqcard b {{ font-size:.93rem; color:var(--wpp-navy); }}
    .eqcard span {{ font-size:.77rem; color:var(--wpp-muted); }}
    .sw {{ display:inline-flex; align-items:center; gap:7px; font-size:.72rem;
        font-weight:600; color:var(--wpp-navy); border:1px solid var(--wpp-line);
        border-radius:8px; padding:6px 11px; background:var(--wpp-white); }}
    .sw i {{ width:14px; height:14px; border-radius:4px; display:inline-block; }}

    /* ---------- TABLAS ---------- */
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {{
        border:1px solid var(--wpp-line); border-radius:12px; overflow:hidden;
        box-shadow:0 2px 8px {rgba(NAVY,.04)}; }}
    div[data-testid="stDataFrame"] table, div[data-testid="stTable"] table {{
        color:var(--wpp-navy) !important; }}
    div[data-testid="stTable"] thead th {{ background:var(--wpp-surf) !important;
        color:var(--wpp-muted) !important; border-color:var(--wpp-line) !important; }}
    div[data-testid="stTable"] tbody tr:nth-child(even) td {{
        background:var(--wpp-surf) !important; }}
    div[data-testid="stTable"] td {{ border-color:var(--wpp-line-soft) !important; }}
    [data-testid="stCaptionContainer"], .stCaption,
    [data-testid="stWidgetLabel"] p {{ color:var(--wpp-muted) !important; }}
    hr {{ border-color:var(--wpp-line) !important; }}
    </style>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# 7 · COMPONENTES DE MARCA
# ═══════════════════════════════════════════════════════════════════════════
def cols(spec, va="center", gap="small"):
    """Columnas con alineación vertical (evita etiquetas sobrepuestas)."""
    try:
        return st.columns(spec, vertical_alignment=va, gap=gap)
    except TypeError:
        try:
            return st.columns(spec, gap=gap)
        except TypeError:
            return st.columns(spec)

def brandbar(sub="Control de Vacaciones"):
    marca = (f'<img src="{LOGO_URI}" alt="WPP Media">' if LOGO_URI else
             f'<span style="font-weight:700;font-size:1.5rem;color:{NAVY}">WPP Media</span>')
    st.markdown(
        f'<div class="brandbar"><div class="brandcard">{marca}'
        f'<div class="brandmeta"><b>{sub}</b>'
        f'<small>People Operations · LATAM</small></div></div>'
        f'<div class="tagmx">MX · CO</div></div>', unsafe_allow_html=True)

def hero(t, s, tag=None):
    extra = f'<div class="tag">{tag}</div>' if tag else ""
    st.markdown(f'<div class="hero"><h1>{t}</h1><p>{s}</p>{extra}</div>',
                unsafe_allow_html=True)

def sect(t):
    st.markdown(f'<div class="sect">{t}</div>', unsafe_allow_html=True)

def chtitle(t, sub=None):
    s = f"<small>{sub}</small>" if sub else ""
    st.markdown(f'<div class="chtitle">{t}{s}</div>', unsafe_allow_html=True)

NOTA_STYLE = {
    "ok":      (TEAL_BG, TEAL),
    "info":    (P629_BG, P629),
    "aviso":   (PERI_BG, PERIWINKLE),
    "critico": (CORN_BG, CORNFLOWER),
    "neutro":  (SURF, NAVY),
}

def nota(txt, kind="neutro"):
    bg, bd = NOTA_STYLE.get(kind, NOTA_STYLE["neutro"])
    st.markdown(f'<div class="nota" style="background:{bg};border-left-color:{bd}">'
                f'{txt}</div>', unsafe_allow_html=True)

def flash(txt, kind="ok"):
    st.session_state.setdefault("_flash", []).append((txt, kind))

def page_header(sub, titulo, desc, tag=None):
    """Encabezado común: marca + hero. En TODAS las vistas."""
    brandbar(sub)
    hero(titulo, desc, tag)
    if not (CFG["existe"] and CFG["primary"] and CFG["font"] and CFG["secundario"]):
        nota("El archivo <b>.streamlit/config.toml</b> no coincide con el tema de "
             "WPP Media. Algunos elementos nativos podrían mostrar colores ajenos a la "
             "marca. Ve a <b>Datos → Auditoría de identidad visual</b> y pulsa "
             "<b>Escribir config.toml corporativo</b>.", "critico")
    for txt, kind in st.session_state.pop("_flash", []):
        nota(txt, kind)

def estilo_fig(fig, leyenda=True, alto=None, x_grid=True, y_grid=True):
    """Ajuste final sobre la plantilla 'wpp'. Sin título interno ⇒ cero solapes."""
    fig.update_layout(
        title=None, template="wpp",
        margin=dict(l=12, r=24, t=48 if leyenda else 16, b=16),
        showlegend=leyenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0,
                    title=None, itemsizing="constant"),
    )
    if alto:
        fig.update_layout(height=alto)
    fig.update_xaxes(gridcolor=LINE_SOFT if x_grid else "rgba(0,0,0,0)")
    fig.update_yaxes(gridcolor=LINE_SOFT if y_grid else "rgba(0,0,0,0)")
    return fig

def tabla_marca(df, pct_cols=(), ancho=True, altura="auto", column_config=None):
    """st.dataframe con barras de porcentaje pintadas por pandas.Styler.

    Esto hace que el color NO dependa del primaryColor del tema (el motivo por el
    que las barras salían naranjas con ProgressColumn)."""
    altura = altura or "auto"          # None ya no es válido en Streamlit 1.5x
    pct = [c for c in pct_cols if c in df.columns]
    cfg = dict(column_config or {})
    try:
        sty = (df.style
                 .format({c: "{:.1f}%" for c in pct})
                 .set_properties(**{"color": NAVY}))
        if pct:
            sty = sty.bar(subset=pct, color=rgba(CORNFLOWER, .42),
                          vmin=0, vmax=100, align="left")
        st.dataframe(sty, use_container_width=ancho, hide_index=True,
                     height=altura, column_config=cfg or None)
        return
    except Exception:
        for c in pct:                       # respaldo si Styler no está disponible
            cfg.setdefault(c, st.column_config.ProgressColumn(
                c, min_value=0, max_value=100, format="%.1f%%"))
        st.dataframe(df, use_container_width=ancho, hide_index=True,
                     height=altura, column_config=cfg or None)

# ═══════════════════════════════════════════════════════════════════════════
# 8 · PERSISTENCIA
# ═══════════════════════════════════════════════════════════════════════════
COLS_EQUIPOS = ["id", "nombre", "manager", "descripcion", "color", "activo"]
COLS_EMPLEADOS = ["id", "equipo_id", "nombre", "pais", "puesto", "email",
                  "fecha_ingreso", "dias_asignados", "activo"]
COLS_VACACIONES = ["id", "empleado_id", "fecha_inicio", "fecha_fin",
                   "anio_derecho", "tipo", "estado", "comentario"]
COLS_FERIADOS = ["id", "pais", "fecha", "descripcion"]

EQUIPO_SEED = {"id": 1, "nombre": "Cris Mora", "manager": "Cristian Mora",
               "descripcion": "Equipo inicial (datos migrados)",
               "color": NAVY, "activo": True}

VERDADEROS = {"true", "1", "1.0", "si", "sí", "yes", "y", "x", "verdadero",
              "activo", "vigente", "v", "t"}
FALSOS = {"false", "0", "0.0", "no", "n", "falso", "inactivo", "baja", "f"}

# ---------------------------------------------------------------------------
# Almacenamiento: Google Sheets (Streamlit Cloud) o CSV locales (tu PC).
#   Si .streamlit/secrets.toml (o los Secrets de Streamlit Cloud) tiene
#   [gcp_service_account] y [sheets], los datos viven en un Google Sheet con
#   una pestaña por tabla: equipos, empleados, vacaciones, feriados.
#   Si no, se usan los CSV de la carpeta data/ como siempre.
# ---------------------------------------------------------------------------
SHEETS_TTL = 30          # segundos que se reutiliza una lectura (cuota de Google)

def usar_sheets():
    try:
        return "gcp_service_account" in st.secrets and "sheets" in st.secrets
    except Exception:                        # no existe secrets.toml
        return False

@st.cache_resource(show_spinner=False)
def _libro():
    import gspread
    gc = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
    cfg = st.secrets["sheets"]
    if cfg.get("spreadsheet_id"):
        return gc.open_by_key(cfg["spreadsheet_id"])
    return gc.open_by_url(cfg["spreadsheet_url"])

def _hoja(path, c):
    """Pestaña del Sheet para una tabla; si no existe se crea con encabezados."""
    import gspread
    nombre = os.path.splitext(os.path.basename(path))[0]
    libro = _libro()
    try:
        return libro.worksheet(nombre)
    except gspread.WorksheetNotFound:
        ws = libro.add_worksheet(title=nombre, rows=1000, cols=max(len(c), 10))
        ws.update(values=[list(c)], range_name="A1", value_input_option="RAW")
        return ws

@st.cache_data(ttl=SHEETS_TTL, show_spinner=False)
def _leer_hoja(path, c):
    vals = _hoja(path, c).get_all_values()
    if not vals:
        return pd.DataFrame(columns=list(c))
    cab = [str(h).strip() for h in vals[0]]
    filas = [(f + [""] * len(cab))[:len(cab)] for f in vals[1:]
             if any(str(x).strip() for x in f)]
    return pd.DataFrame(filas, columns=cab, dtype=str)

def _escribir_hoja(df, path):
    ws = _hoja(path, list(df.columns))
    d = df.astype(object).where(df.notna(), "").astype(str)
    vals = [list(df.columns)] + d.values.tolist()
    if ws.row_count < len(vals):
        ws.add_rows(len(vals) - ws.row_count + 100)
    # Primero se escribe y DESPUÉS se limpian las filas sobrantes: si falla la
    # conexión a mitad, nunca queda la hoja vacía.
    ws.update(values=vals, range_name="A1", value_input_option="RAW")
    if ws.row_count > len(vals):
        ws.batch_clear([f"A{len(vals) + 1}:Z{ws.row_count}"])
    _leer_hoja.clear()

def _error_sheets(accion, e):
    st.error(f"No se pudo {accion} en Google Sheets: {type(e).__name__}: {e}. "
             "Revisa los Secrets (cuenta de servicio y spreadsheet_id) y que el "
             "Sheet esté compartido como Editor con el correo de la cuenta de "
             "servicio. Si es un límite de cuota, espera un minuto y recarga.")
    st.stop()

def _ensure_files():
    if usar_sheets():
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    for path, c in [(F_EQUIPOS, COLS_EQUIPOS), (F_EMPLEADOS, COLS_EMPLEADOS),
                    (F_VACACIONES, COLS_VACACIONES), (F_FERIADOS, COLS_FERIADOS)]:
        if not os.path.exists(path):
            pd.DataFrame(columns=c).to_csv(path, index=False)

def load_csv(path, c):
    if usar_sheets():
        try:
            df = _leer_hoja(path, tuple(c))
        except Exception as e:
            _error_sheets("leer", e)
    else:
        _ensure_files()
        try:
            df = pd.read_csv(path, dtype=str, keep_default_na=False,
                             encoding="utf-8-sig")
        except (pd.errors.EmptyDataError, FileNotFoundError):
            df = pd.DataFrame(columns=c)
    for col in c:
        if col not in df.columns:
            df[col] = ""
    return df[c].copy()

def save_csv(df, path):
    if usar_sheets():
        try:
            _escribir_hoja(df, path)
        except Exception as e:
            _error_sheets("guardar", e)
    else:
        df.to_csv(path, index=False)

def _txt(s):
    return (s.astype("object").where(s.notna(), "").astype(str)
            .replace({"nan": "", "None": "", "<NA>": "", "NaN": ""}).str.strip())

def _bool(serie, default=True):
    def conv(v):
        if isinstance(v, bool):
            return v
        s = str(v).strip().lower()
        if s in VERDADEROS:
            return True
        if s in FALSOS:
            return False
        return default
    return serie.apply(conv)

def _color_valido(c, fallback=NAVY):
    c = (c or "").strip()
    return c if c.upper() in [p.upper() for p in PALETA_OFICIAL] else fallback

def get_equipos():
    df = load_csv(F_EQUIPOS, COLS_EQUIPOS)
    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    for c in ["nombre", "manager", "descripcion", "color"]:
        df[c] = _txt(df[c])
    df["activo"] = _bool(df["activo"], default=True)
    df = df[(df["nombre"] != "") & (df["id"] > 0)]
    if df.empty:
        df = pd.DataFrame([EQUIPO_SEED])
    df = df.reset_index(drop=True)
    df["color"] = [_color_valido(c, PALETA_SERIES[i % len(PALETA_SERIES)])
                   for i, c in enumerate(df["color"])]
    return df.sort_values("id").reset_index(drop=True)

def save_equipos(df):
    d = df.copy()
    d["id"] = pd.to_numeric(d["id"], errors="coerce").fillna(0).astype(int)
    d["activo"] = _bool(d["activo"], True).map({True: "True", False: "False"})
    for c in ["nombre", "manager", "descripcion", "color"]:
        d[c] = _txt(d[c])
    d["color"] = [_color_valido(c) for c in d["color"]]
    save_csv(d[COLS_EQUIPOS], F_EQUIPOS)

def get_empleados():
    df = load_csv(F_EMPLEADOS, COLS_EMPLEADOS)
    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df["equipo_id"] = pd.to_numeric(df["equipo_id"], errors="coerce").fillna(0).astype(int)
    df["dias_asignados"] = pd.to_numeric(df["dias_asignados"],
                                         errors="coerce").fillna(0).astype(int)
    df["activo"] = _bool(df["activo"], default=True)     # vacío = ACTIVO
    for c in ["nombre", "pais", "puesto", "email", "fecha_ingreso"]:
        df[c] = _txt(df[c])
    df.loc[~df["pais"].isin(PAISES), "pais"] = PAISES[0]
    return df.reset_index(drop=True)

def save_empleados(df):
    d = df.copy()
    d["activo"] = _bool(d["activo"], default=True).map({True: "True", False: "False"})
    for c in ["id", "equipo_id", "dias_asignados"]:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0).astype(int)
    save_csv(d[COLS_EMPLEADOS], F_EMPLEADOS)

def get_vacaciones():
    df = load_csv(F_VACACIONES, COLS_VACACIONES)
    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df["empleado_id"] = pd.to_numeric(df["empleado_id"],
                                      errors="coerce").fillna(0).astype(int)
    for c in ["tipo", "estado", "comentario"]:
        df[c] = _txt(df[c])
    df.loc[~df["tipo"].isin(TIPOS), "tipo"] = TIPOS[0]
    df.loc[~df["estado"].isin(ESTADOS), "estado"] = ESTADOS[1]
    if not df.empty:
        df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce").dt.date
        df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce").dt.date
        df = df.dropna(subset=["fecha_inicio", "fecha_fin"])
        ad = pd.to_numeric(df["anio_derecho"], errors="coerce")
        df["anio_derecho"] = ad.fillna(
            pd.Series([d.year for d in df["fecha_inicio"]], index=df.index)).astype(int)
    else:
        df["anio_derecho"] = pd.Series(dtype=int)
    return df.reset_index(drop=True)

def get_feriados():
    df = load_csv(F_FERIADOS, COLS_FERIADOS)
    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    for c in ["pais", "descripcion"]:
        df[c] = _txt(df[c])
    df.loc[~df["pais"].isin(PAISES), "pais"] = PAISES[0]
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date
        df = df.dropna(subset=["fecha"])
    return df.reset_index(drop=True)

def next_id(df):
    return 1 if df.empty else int(pd.to_numeric(df["id"],
                                                errors="coerce").fillna(0).max()) + 1

def renumerar_feriados(df):
    if df.empty:
        return df
    d = df.copy()
    d["_p"] = d["pais"].apply(lambda p: PAISES.index(p) if p in PAISES else 99)
    d["_f"] = pd.to_datetime(d["fecha"], errors="coerce")
    d = d.drop_duplicates(subset=["pais", "fecha"], keep="first")
    d = d.sort_values(["_p", "_f"]).drop(columns=["_p", "_f"]).reset_index(drop=True)
    d["id"] = range(1, len(d) + 1)
    return d

def save_feriados(df):
    save_csv(renumerar_feriados(df), F_FERIADOS)

def migrar_a_equipos():
    _ensure_files()
    raw = load_csv(F_EQUIPOS, COLS_EQUIPOS)
    raw["id"] = pd.to_numeric(raw["id"], errors="coerce").fillna(0).astype(int)
    if raw[(raw["id"] > 0) & (_txt(raw["nombre"]) != "")].empty:
        save_equipos(pd.DataFrame([EQUIPO_SEED]))
    eq = get_equipos()
    validos, defecto = set(eq["id"]), int(eq["id"].min())
    em = get_empleados()
    if not em.empty:
        mal = ~em["equipo_id"].isin(validos)
        if mal.any():
            em.loc[mal, "equipo_id"] = defecto
            save_empleados(em)

def bump(k):
    st.session_state[k] = st.session_state.get(k, 0) + 1

def ver(k):
    return st.session_state.setdefault(k, 0)

# ═══════════════════════════════════════════════════════════════════════════
# 9 · LÓGICA DE NEGOCIO (sin cambios funcionales)
# ═══════════════════════════════════════════════════════════════════════════
def feriados_por_pais(df):
    out = {p: set() for p in PAISES}
    for _, r in df.iterrows():
        out.setdefault(r["pais"], set()).add(r["fecha"])
    return out

def dias_habiles(ini, fin, fset):
    if ini is None or fin is None or fin < ini:
        return 0
    n, d = 0, ini
    while d <= fin:
        if d.weekday() < 5 and d not in fset:
            n += 1
        d += timedelta(days=1)
    return n

def dias_naturales(ini, fin):
    return 0 if fin < ini else (fin - ini).days + 1

def dh_de_fila(r, paises, fer_dict):
    return dias_habiles(r["fecha_inicio"], r["fecha_fin"],
                        fer_dict.get(paises.get(r["empleado_id"], ""), set()))

def resumen_empleados(emp, vac, fer, anio, paises_f=None, solo_activos=False, eq_nom=None):
    fset = feriados_por_pais(fer)
    e_df = emp.copy()
    if paises_f:
        e_df = e_df[e_df["pais"].isin(paises_f)]
    if solo_activos:
        e_df = e_df[e_df["activo"]]
    filas = []
    for _, e in e_df.iterrows():
        v = vac[(vac["empleado_id"] == e["id"]) & (vac["tipo"] == "Vacaciones") &
                (vac["anio_derecho"] == anio)]
        tom = apr = sol = 0
        for _, r in v.iterrows():
            d = dias_habiles(r["fecha_inicio"], r["fecha_fin"], fset.get(e["pais"], set()))
            if r["estado"] == "Tomada":
                tom += d
            elif r["estado"] == "Aprobada":
                apr += d
            elif r["estado"] == "Solicitada":
                sol += d
        otras = vac[(vac["empleado_id"] == e["id"]) & (vac["tipo"] != "Vacaciones") &
                    (vac["estado"].isin(ESTADOS_CUENTAN))]
        otras_d = sum(dias_habiles(r["fecha_inicio"], r["fecha_fin"],
                                   fset.get(e["pais"], set()))
                      for _, r in otras.iterrows()
                      if r["fecha_inicio"].year == anio or r["fecha_fin"].year == anio)
        comp, asg = tom + apr, int(e["dias_asignados"])
        filas.append({
            "ID": e["id"], "Equipo": (eq_nom or {}).get(e["equipo_id"], "—"),
            "Colaborador": e["nombre"], "Pais": e["pais"],
            "País": COD_PAIS.get(e["pais"], ""), "Puesto": e["puesto"],
            "Días asignados": asg, "Tomados": tom, "Proyectados": apr,
            "En solicitud": sol, "Comprometidos": comp, "Saldo": asg - comp,
            "% consumido": round(100 * comp / asg, 1) if asg else 0.0,
            "Otras ausencias": otras_d, "Activo": bool(e["activo"]),
            "Estatus": "Activo" if e["activo"] else "Inactivo",
        })
    return pd.DataFrame(filas)

def pivot_por_anio(emp, vac, fer, paises_f=None, estados=ESTADOS_CUENTAN):
    fset = feriados_por_pais(fer)
    nom = dict(zip(emp["id"], emp["nombre"]))
    pai = dict(zip(emp["id"], emp["pais"]))
    reg = []
    for _, r in vac[(vac["tipo"] == "Vacaciones") &
                    (vac["estado"].isin(estados))].iterrows():
        eid = r["empleado_id"]
        if eid not in nom:
            continue
        if paises_f and pai.get(eid) not in paises_f:
            continue
        reg.append({"Colaborador": nom[eid], "Año de derecho": int(r["anio_derecho"]),
                    "Días": dias_habiles(r["fecha_inicio"], r["fecha_fin"],
                                         fset.get(pai.get(eid, ""), set()))})
    if not reg:
        return pd.DataFrame(), pd.DataFrame()
    df = pd.DataFrame(reg)
    pv = df.pivot_table(index="Colaborador", columns="Año de derecho", values="Días",
                        aggfunc="sum", fill_value=0)
    pv.columns = [str(c) for c in pv.columns]
    pv["TOTAL"] = pv.sum(axis=1)
    largo = df.groupby(["Colaborador", "Año de derecho"], as_index=False)["Días"].sum()
    largo["Año de derecho"] = largo["Año de derecho"].astype(str)
    return pv.reset_index(), largo

def dias_por_mes(emp, vac, fer, anio_cal, paises_f=None,
                 estados=("Tomada", "Aprobada", "Solicitada")):
    fset = feriados_por_pais(fer)
    pai = dict(zip(emp["id"], emp["pais"]))
    rows = []
    for m in range(1, 13):
        ini = date(anio_cal, m, 1)
        fin = date(anio_cal, m, calendar.monthrange(anio_cal, m)[1])
        acc = {e: 0 for e in estados}
        for _, r in vac.iterrows():
            eid = r["empleado_id"]
            if eid not in pai or r["estado"] not in estados:
                continue
            if paises_f and pai[eid] not in paises_f:
                continue
            if r["fecha_fin"] < ini or r["fecha_inicio"] > fin:
                continue
            acc[r["estado"]] += dias_habiles(max(r["fecha_inicio"], ini),
                                             min(r["fecha_fin"], fin),
                                             fset.get(pai[eid], set()))
        for e, v in acc.items():
            rows.append({"Mes": MESES_ES[m - 1][:3], "MesNum": m, "Estado": e, "Días": v})
    return pd.DataFrame(rows).sort_values("MesNum")

def dias_traslape(emp, vac, desde, hasta, paises_f=None, umbral=2):
    nom = dict(zip(emp["id"], emp["nombre"]))
    pai = dict(zip(emp["id"], emp["pais"]))
    conteo = {}
    for _, r in vac[vac["estado"].isin(ESTADOS_CUENTAN)].iterrows():
        eid = r["empleado_id"]
        if eid not in nom:
            continue
        if paises_f and pai.get(eid) not in paises_f:
            continue
        d, end = max(r["fecha_inicio"], desde), min(r["fecha_fin"], hasta)
        while d <= end:
            if d.weekday() < 5:
                conteo.setdefault(d, set()).add(nom[eid])
            d += timedelta(days=1)
    out = [{"Fecha": d, "Personas": len(p), "Quiénes": ", ".join(sorted(p))}
           for d, p in conteo.items() if len(p) >= umbral]
    return pd.DataFrame(out).sort_values("Fecha") if out else pd.DataFrame()

def expandir_dias(vac, emp, cmap):
    mapa = {}
    nom = dict(zip(emp["id"], emp["nombre"]))
    pai = dict(zip(emp["id"], emp["pais"]))
    for _, r in vac.iterrows():
        eid = r["empleado_id"]
        if eid not in nom:
            continue
        d = r["fecha_inicio"]
        while d <= r["fecha_fin"]:
            mapa.setdefault(d, []).append({
                "nombre": nom[eid], "pais": pai.get(eid, ""), "estado": r["estado"],
                "tipo": r["tipo"], "anio": int(r["anio_derecho"]),
                "color": cmap.get(eid, NAVY)})
            d += timedelta(days=1)
    return mapa

def color_map_personas(emp):
    return {eid: PALETA_PERSONAS[i % len(PALETA_PERSONAS)]
            for i, eid in enumerate(emp["id"].tolist())}

def hay_traslape(df, eid, ini, fin, excluir_id=None):
    d = df[df["empleado_id"] == eid]
    if excluir_id is not None:
        d = d[d["id"] != excluir_id]
    return not d[(d["fecha_inicio"] <= fin) & (d["fecha_fin"] >= ini)].empty

# --------- Feriados oficiales ---------
def _nth_weekday(a, m, wd, n):
    d = date(a, m, 1)
    d += timedelta(days=(wd - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)

def _pascua(anio):
    a = anio % 19
    b, c = divmod(anio, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(anio, mes, dia)

def _lunes_siguiente(d):
    return d if d.weekday() == 0 else d + timedelta(days=(7 - d.weekday()))

def feriados_mexico(a):
    return [(date(a, 1, 1), "Año Nuevo"),
            (_nth_weekday(a, 2, 0, 1), "Día de la Constitución"),
            (_nth_weekday(a, 3, 0, 3), "Natalicio de Benito Juárez"),
            (date(a, 5, 1), "Día del Trabajo"),
            (date(a, 9, 16), "Independencia de México"),
            (_nth_weekday(a, 11, 0, 3), "Revolución Mexicana"),
            (date(a, 12, 25), "Navidad")]

def feriados_colombia(a):
    p = _pascua(a)
    fijos = [(date(a, 1, 1), "Año Nuevo"), (date(a, 5, 1), "Día del Trabajo"),
             (date(a, 7, 20), "Independencia"), (date(a, 8, 7), "Batalla de Boyacá"),
             (date(a, 12, 8), "Inmaculada Concepción"), (date(a, 12, 25), "Navidad")]
    moviles = [(date(a, 1, 6), "Reyes Magos"), (date(a, 3, 19), "San José"),
               (date(a, 6, 29), "San Pedro y San Pablo"), (date(a, 8, 15), "Asunción"),
               (date(a, 10, 12), "Día de la Raza"), (date(a, 11, 1), "Todos los Santos"),
               (date(a, 11, 11), "Independencia de Cartagena")]
    pascuales = [(p - timedelta(days=3), "Jueves Santo"),
                 (p - timedelta(days=2), "Viernes Santo"),
                 (p + timedelta(days=43), "Ascensión del Señor"),
                 (p + timedelta(days=64), "Corpus Christi"),
                 (p + timedelta(days=71), "Sagrado Corazón")]
    return fijos + [(_lunes_siguiente(d), n) for d, n in moviles] + pascuales

# ═══════════════════════════════════════════════════════════════════════════
# 10 · CALENDARIO
# ═══════════════════════════════════════════════════════════════════════════
CAL_CSS = f"""
<style>
.calwrap{{border:1px solid {LINE};border-radius:13px;overflow:hidden;
         box-shadow:0 8px 22px {rgba(NAVY,.07)};background:{WHITE};margin-top:6px;}}
table.cal{{width:100%;border-collapse:collapse;font-family:{FONT};}}
table.cal th{{background:{NAVY};color:{WHITE};padding:10px 6px;font-size:.72rem;
             font-weight:600;letter-spacing:1.1px;text-transform:uppercase;
             border:none;border-bottom:3px solid {LIME};}}
table.cal td{{vertical-align:top;height:106px;width:14.28%;border:1px solid {LINE_SOFT};
             padding:5px 6px;background:{WHITE};}}
td.out{{background:{WHITE};}} td.out .dn{{color:{GHOST};}}
td.wknd{{background:{rgba(P629,.07)};}}
td.past{{background:{SURF};}} td.past .dn{{color:{FAINT};}}
td.wknd.past{{background:{rgba(NAVY,.075)};}}
td.today{{box-shadow:inset 0 0 0 2px {NAVY};background:{P629_BG_LT} !important;}}
.dn{{font-weight:700;font-size:.84rem;color:{NAVY};margin-bottom:4px;
    display:flex;align-items:center;gap:5px;}}
.dn .bul{{background:{NAVY};color:{LIME};border-radius:50%;width:21px;height:21px;
         display:inline-flex;align-items:center;justify-content:center;font-size:.69rem;}}
.fchip{{display:block;font-size:.61rem;font-weight:700;border-radius:4px;padding:1px 5px;
       margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
       color:{NAVY};}}
.chip{{display:block;font-size:.64rem;font-weight:600;border-radius:5px;padding:2px 6px;
      margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
      border-left:3px solid {NAVY};}}
.leg{{display:flex;flex-wrap:wrap;gap:7px;margin:6px 0 10px;}}
.leg span{{font-size:.70rem;font-weight:600;padding:5px 12px;border-radius:30px;
          border:1px solid {LINE};color:{NAVY};}}
</style>
"""

def leyenda(ev):
    h = '<div class="leg">'
    for e in ESTADOS:
        if e in ev:
            bg, tx, strong = ESTADO_STYLE[e]
            h += f'<span style="background:{bg};border-color:{strong}">{e}</span>'
    for p in PAISES:
        h += (f'<span style="background:{FERIADO_BG[p]};'
              f'border-color:{FERIADO_COLOR[p]}">Feriado {COD_PAIS[p]}</span>')
    h += (f'<span style="background:{SURF};color:{MUTED}">Días pasados</span>'
          f'<span style="background:{P629_BG_LT};border-color:{NAVY}">Hoy</span></div>')
    return h

def render_calendario(anio, mes, mapa, fer_dict, filtro_pais, mostrar_anio=False):
    hoy = date.today()
    fer_all = {}
    for p, s in fer_dict.items():
        for f in s:
            fer_all.setdefault(f, []).append(p)

    html = CAL_CSS + '<div class="calwrap"><table class="cal"><tr>'
    html += "".join(f"<th>{d}</th>" for d in DIAS_ES) + "</tr>"

    for semana in calendar.Calendar(firstweekday=0).monthdatescalendar(anio, mes):
        html += "<tr>"
        for d in semana:
            cls, style = [], ""
            in_month = (d.month == mes and d.year == anio)
            if not in_month:
                cls.append("out")
            else:
                if d.weekday() >= 5:
                    cls.append("wknd")
                if d < hoy:
                    cls.append("past")
                if d == hoy:
                    cls.append("today")
                pf = fer_all.get(d, [])
                if len(pf) == 1:
                    style = (f"background:{FERIADO_BG[pf[0]]} !important;"
                             f"border-left:4px solid {FERIADO_COLOR[pf[0]]} !important;")
                elif len(pf) > 1:
                    style = (f"background:linear-gradient(135deg,{FERIADO_BG['México']} 0%,"
                             f"{FERIADO_BG['México']} 48%,{FERIADO_BG['Colombia']} 52%,"
                             f"{FERIADO_BG['Colombia']} 100%) !important;"
                             f"border-left:4px solid {LIME} !important;")
            num = (f'<span class="bul">{d.day}</span>'
                   if (d == hoy and in_month) else str(d.day))
            html += f'<td class="{" ".join(cls)}" style="{style}"><div class="dn">{num}</div>'
            if in_month:
                for p in fer_all.get(d, []):
                    html += (f'<span class="fchip" style="background:{FERIADO_COLOR[p]};'
                             f'border:1px solid {FERIADO_COLOR[p]}">'
                             f'Feriado {COD_PAIS[p]}</span>')
                for it in mapa.get(d, []):
                    if filtro_pais and it["pais"] not in filtro_pais:
                        continue
                    bg, tx, _ = ESTADO_STYLE.get(it["estado"], (SURF, NAVY, NAVY))
                    pre = "" if it["tipo"] == "Vacaciones" else "· "
                    suf = f' <b>{str(it["anio"])[2:]}</b>' if mostrar_anio else ""
                    html += (f'<span class="chip" style="background:{bg};color:{tx};'
                             f'border-left-color:{it["color"]}" '
                             f'title="{it["nombre"]} — {it["tipo"]} ({it["estado"]}) '
                             f'· Año de derecho {it["anio"]}">{pre}{it["nombre"]}{suf}</span>')
            html += "</td>"
        html += "</tr>"
    html += "</table></div>"
    st.markdown(html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# 11 · ARRANQUE
# ═══════════════════════════════════════════════════════════════════════════
inject_css()
_ensure_files()
migrar_a_equipos()

equipos = get_equipos()
emp_all = get_empleados()
vac_all = get_vacaciones()
fer = get_feriados()
fer_dict = feriados_por_pais(fer)

eq_nom = dict(zip(equipos["id"], equipos["nombre"]))
eq_mgr = dict(zip(equipos["id"], equipos["manager"]))
eq_col = dict(zip(equipos["id"], equipos["color"]))
nom_eq = {v: k for k, v in eq_nom.items()}

# ---------------- SIDEBAR ----------------
if LOGO_URI:
    st.sidebar.markdown(
        f'<div class="sidecard"><img src="{LOGO_URI}" alt="WPP Media"></div>',
        unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="sidecard"><div class="fb">WPP Media</div></div>',
                        unsafe_allow_html=True)

st.sidebar.markdown(
    f'<div style="font-weight:700;font-size:.94rem;color:{NAVY};line-height:1.2">'
    f'Control de Vacaciones'
    f'<div style="font-weight:500;font-size:.68rem;color:{MUTED};letter-spacing:1.1px;'
    f'text-transform:uppercase;margin-top:4px">México · Colombia</div></div>'
    f'<div style="height:3px;width:46px;background:{LIME};border-radius:3px;'
    f'margin:11px 0 6px"></div>', unsafe_allow_html=True)


st.sidebar.markdown(
    f'<div style="font-size:.67rem;font-weight:700;color:{MUTED};letter-spacing:1.2px;'
    f'margin:14px 0 2px">EQUIPO</div>', unsafe_allow_html=True)

op_eq = [str(i) for i in equipos["id"].tolist()] + [TODOS]
if st.session_state.get("scope_eq") not in op_eq:
    st.session_state.scope_eq = op_eq[0]

def fmt_eq(v):
    if v == TODOS:
        return "Todos los equipos (consolidado)"
    i = int(v)
    mgr = eq_mgr.get(i, "")
    return f'{eq_nom.get(i, "?")}' + (f" · {mgr}" if mgr else "")

st.sidebar.selectbox("Equipo", op_eq, format_func=fmt_eq, key="scope_eq",
                     label_visibility="collapsed")
scope = st.session_state.scope_eq
modo_todos = scope == TODOS
equipo_id = None if modo_todos else int(scope)

with st.sidebar.expander("Crear equipo nuevo"):
    with st.form("f_eq_side", clear_on_submit=True):
        e_nom = st.text_input("Nombre del equipo", placeholder="Ej. Performance LATAM")
        e_mgr = st.text_input("Manager", placeholder="Ej. Ana Pérez")
        e_col = st.selectbox("Color de marca", PALETA_SERIES, index=1,
                             format_func=lambda c: NOMBRE_COLOR.get(c, c))
        if st.form_submit_button("Crear equipo", type="primary"):
            if not e_nom.strip() or not e_mgr.strip():
                flash("Nombre y manager son obligatorios.", "critico")
            elif e_nom.strip().lower() in [n.lower() for n in eq_nom.values()]:
                flash("Ya existe un equipo con ese nombre.", "aviso")
            else:
                base = get_equipos()
                nid = next_id(base)
                save_equipos(pd.concat([base, pd.DataFrame([{
                    "id": nid, "nombre": e_nom.strip(), "manager": e_mgr.strip(),
                    "descripcion": "", "color": e_col, "activo": True}])],
                    ignore_index=True))
                st.session_state.scope_eq = str(nid)
                bump("v_eq")
                flash(f"Equipo <b>{e_nom}</b> creado y seleccionado.", "ok")
            st.rerun()

st.sidebar.divider()
seccion = st.sidebar.radio("Navegación", [
    "Dashboard", "Equipos", "Personas", "Vacaciones", "Calendario",
    "Feriados México", "Feriados Colombia", "Datos"],
    label_visibility="collapsed", key="nav_seccion")

st.sidebar.divider()
st.sidebar.number_input("Año de derecho / ejercicio", 2015, 2100,
                        value=st.session_state.get("anio_view", date.today().year),
                        step=1, key="anio_view")
anio_sel = int(st.session_state.anio_view)

# ---------------- ÁMBITO ----------------
if modo_todos:
    emp = emp_all.copy()
    etiqueta_eq = "Todos los equipos"
else:
    emp = emp_all[emp_all["equipo_id"] == equipo_id].copy()
    etiqueta_eq = f'{eq_nom.get(equipo_id,"?")} · Manager: {eq_mgr.get(equipo_id,"—")}'

vac = (vac_all[vac_all["empleado_id"].isin(emp["id"])].copy()
       if not emp.empty else vac_all.iloc[0:0].copy())

cmap = color_map_personas(emp_all)
nombres = dict(zip(emp_all["id"], emp_all["nombre"]))
paises = dict(zip(emp_all["id"], emp_all["pais"]))
emp_eq = dict(zip(emp_all["id"], emp_all["equipo_id"]))

st.sidebar.markdown(
    f'<div style="font-size:.74rem;color:{MUTED};line-height:1.75;'
    f'border-left:3px solid {LIME};padding-left:11px;margin-top:4px">'
    f'<b style="color:{NAVY}">Ámbito actual</b><br>{etiqueta_eq}<br>'
    f'{len(emp)} personas · {int(emp["activo"].sum()) if not emp.empty else 0} activas<br>'
    f'{len(vac)} periodos · {len(fer)} feriados<br>'
    f'Hoy: {date.today():%d/%m/%Y}<br>'
    f'Datos: {"Google Sheets (compartido)" if usar_sheets() else "CSV local"}</div>',
    unsafe_allow_html=True)

ANIOS_OPC = list(range(anio_sel - 4, anio_sel + 3))
anios_datos = (sorted(set(int(a) for a in vac_all["anio_derecho"].tolist()))
               if not vac_all.empty else [])
anios_disp = sorted(set(anios_datos + [date.today().year - 1, date.today().year,
                                       date.today().year + 1, anio_sel]))

def set_anio(a):
    st.session_state.anio_view = int(a)

def exige_equipo(msg="Selecciona un equipo específico en la barra lateral."):
    if modo_todos:
        nota("Estás en modo consolidado. " + msg, "info")
        return False
    return True

# ═══════════════════════════ DASHBOARD ═══════════════════════════
if seccion == "Dashboard":
    page_header("Panel de control de vacaciones",
                f"Panel de control <em>·</em> {anio_sel}",
                f"Saldos, proyecciones y cobertura · datos al {date.today():%d/%m/%Y}",
                etiqueta_eq)

    if emp.empty:
        nota("Este equipo aún no tiene personas. Ve a <b>Personas</b> para agregar "
             "la primera.", "info")
        st.stop()

    n = cols([0.6, 2.0, 0.6, 1.0, 4.0])
    n[0].button("◀", key="a_prev", on_click=set_anio, args=(anio_sel - 1,),
                use_container_width=True, help="Año anterior")
    n[1].markdown(f'<div class="navtitle">{anio_sel}<small>AÑO DE DERECHO</small></div>',
                  unsafe_allow_html=True)
    n[2].button("▶", key="a_next", on_click=set_anio, args=(anio_sel + 1,),
                use_container_width=True, help="Año siguiente")
    n[3].button("Hoy", key="a_hoy", on_click=set_anio, args=(date.today().year,),
                use_container_width=True)

    f = cols([1.2, 1.8, 1.3, 2.7], va="bottom")
    salto = f[0].selectbox("Ir al año", ["—"] + [str(a) for a in anios_disp],
                           key="db_salto")
    if salto != "—" and int(salto) != anio_sel:
        set_anio(int(salto))
        st.rerun()
    pais_f = f[1].multiselect("País", PAISES, default=PAISES, key="db_pais") or PAISES
    incluir_inact = f[2].toggle("Incluir inactivos", value=False, key="db_inact")

    res_all = resumen_empleados(emp, vac, fer, anio_sel, paises_f=pais_f, eq_nom=eq_nom)
    res = res_all if incluir_inact else res_all[res_all["Activo"]]

    if res_all.empty:
        nota(f"No hay personas en los países seleccionados: {', '.join(pais_f)}.", "aviso")
        st.stop()
    if res.empty:
        nota("<b>Todas las personas están marcadas como inactivas</b>, por eso los "
             "indicadores aparecen en cero.", "critico")
        c1, c2 = cols([1, 3])
        if c1.button("Activar a todos", type="primary"):
            base = get_empleados()
            base.loc[base["id"].isin(emp["id"]), "activo"] = True
            save_empleados(base)
            bump("v_emp")
            flash("Todas las personas del equipo quedaron activas.", "ok")
            st.rerun()
        with c2:
            nota("También puedes activar el interruptor <b>Incluir inactivos</b>.", "info")
        st.stop()

    asg = int(res["Días asignados"].sum())
    tom = int(res["Tomados"].sum())
    pro = int(res["Proyectados"].sum())
    sol = int(res["En solicitud"].sum())
    sal = int(res["Saldo"].sum())
    pct = round(100 * (tom + pro) / asg, 1) if asg else 0.0

    k = st.columns(6)
    k[0].metric("Personas", len(res),
                delta=f'{int(res_all["Activo"].sum())} de {len(res_all)} activas',
                delta_color="off")
    k[1].metric(f"Asignados {anio_sel}", asg)
    k[2].metric("Tomados", tom)
    k[3].metric("Proyectados", pro)
    k[4].metric("En solicitud", sol)
    k[5].metric("Saldo", sal, delta=f"{100-pct:.1f}% sin usar", delta_color="off")

    st.markdown(f'<div style="font-size:.78rem;color:{MUTED};margin:10px 0 4px">'
                f'Consumo global del ejercicio {anio_sel}: '
                f'<b style="color:{NAVY}">{pct}%</b> ({tom+pro} de {asg} días)</div>',
                unsafe_allow_html=True)
    st.progress(min(pct / 100, 1.0))

    sect("Alertas y seguimiento")
    hoy = date.today()
    al = []
    for _, r in res[res["Saldo"] < 0].iterrows():
        al.append((f'<b>{r["Colaborador"]}</b> excede su saldo {anio_sel} por '
                   f'<b>{abs(int(r["Saldo"]))} día(s)</b>.', "critico"))
    sin_uso = res[(res["Comprometidos"] == 0) & (res["En solicitud"] == 0)]
    if not sin_uso.empty:
        al.append((f'Sin días registrados en {anio_sel}: '
                   f'<b>{", ".join(sin_uso["Colaborador"])}</b>.', "aviso"))
    if hoy.month >= 9 and anio_sel <= hoy.year:
        riesgo = res[(res["% consumido"] < 50) & (res["Días asignados"] > 0)]
        if not riesgo.empty:
            al.append((f'Menos del 50% consumido y ya estamos en '
                       f'{MESES_ES[hoy.month-1]}: '
                       f'<b>{", ".join(riesgo["Colaborador"])}</b>.', "aviso"))
    pend = vac[vac["estado"] == "Solicitada"]
    if not pend.empty:
        al.append((f'Hay <b>{len(pend)} solicitud(es)</b> pendientes de aprobación.',
                   "info"))
    tras = dias_traslape(emp, vac, hoy, hoy + timedelta(days=60), pais_f, umbral=2)
    if not tras.empty:
        px0 = tras.iloc[0]
        al.append((f'Cobertura: <b>{len(tras)} día(s)</b> en los próximos 60 con 2 o más '
                   f'personas ausentes (el más próximo {px0["Fecha"]:%d/%m} → '
                   f'{px0["Quiénes"]}).', "info"))
    if al:
        for txt, kind in al:
            nota(txt, kind)
    else:
        nota("Todo en orden: sin sobregiros, sin pendientes y buena cobertura.", "ok")

    col1, col2 = st.columns(2)
    with col1:
        sect("Ausentes hoy")
        h = vac[(vac["fecha_inicio"] <= hoy) & (vac["fecha_fin"] >= hoy) &
                (vac["estado"].isin(ESTADOS_CUENTAN)) &
                (vac["empleado_id"].isin(res["ID"]))]
        if h.empty:
            nota("Todo el equipo está disponible hoy.", "ok")
        else:
            for _, r in h.iterrows():
                c = cmap.get(r["empleado_id"], NAVY)
                bg, tx, _ = ESTADO_STYLE[r["estado"]]
                eqt = (f'<span class="pill" style="background:{P629_BG};color:{NAVY}">'
                       f'{eq_nom.get(emp_eq.get(r["empleado_id"]),"")}</span>'
                       if modo_todos else "")
                st.markdown(
                    f'<div class="row" style="border-left-color:{c}"><div style="flex:1">'
                    f'<span class="nm">{nombres.get(r["empleado_id"],"?")}</span> '
                    f'<span class="pill" style="background:{bg};color:{tx}">'
                    f'{r["tipo"]}</span>'
                    f'<span class="pill" style="background:{SURF};color:{MUTED}">'
                    f'Año {int(r["anio_derecho"])}</span>{eqt}<br>'
                    f'<span class="dt">Regresa el '
                    f'{(r["fecha_fin"]+timedelta(days=1)):%d/%m/%Y}</span></div></div>',
                    unsafe_allow_html=True)
    with col2:
        sect("Próximas ausencias (30 días)")
        p = vac[(vac["fecha_inicio"] > hoy) &
                (vac["fecha_inicio"] <= hoy + timedelta(days=30)) &
                (vac["estado"].isin(["Aprobada", "Solicitada"])) &
                (vac["empleado_id"].isin(res["ID"]))].sort_values("fecha_inicio")
        if p.empty:
            nota("Sin ausencias programadas en los próximos 30 días.", "info")
        else:
            for _, r in p.iterrows():
                c = cmap.get(r["empleado_id"], NAVY)
                bg, tx, _ = ESTADO_STYLE[r["estado"]]
                eqt = (f'<span class="pill" style="background:{P629_BG};color:{NAVY}">'
                       f'{eq_nom.get(emp_eq.get(r["empleado_id"]),"")}</span>'
                       if modo_todos else "")
                st.markdown(
                    f'<div class="row" style="border-left-color:{c}"><div style="flex:1">'
                    f'<span class="nm">{nombres.get(r["empleado_id"],"?")}</span> '
                    f'<span class="pill" style="background:{bg};color:{tx}">'
                    f'{r["estado"]}</span>'
                    f'<span class="pill" style="background:{SURF};color:{MUTED}">'
                    f'Año {int(r["anio_derecho"])}</span>{eqt}<br>'
                    f'<span class="dt">{r["fecha_inicio"]:%d/%m} — '
                    f'{r["fecha_fin"]:%d/%m} · en '
                    f'{(r["fecha_inicio"]-hoy).days} días</span></div></div>',
                    unsafe_allow_html=True)

    sect("Analítica visual")
    tabs_lbl = ["Por persona", "Consumo", "Estacionalidad", "Por país", "Por año"]
    if modo_todos:
        tabs_lbl.append("Por equipo")
    tb = st.tabs(tabs_lbl)

    with tb[0]:
        chtitle(f"Días asignados vs. usados — ejercicio {anio_sel}",
                "Las barras suman el total asignado de cada persona")
        base = res[["Colaborador", "Tomados", "Proyectados", "En solicitud",
                    "Saldo"]].copy()
        base["Saldo"] = base["Saldo"].clip(lower=0)
        pl = base.melt(id_vars="Colaborador", var_name="Concepto", value_name="Días")
        if pl["Días"].sum() == 0:
            nota(f"Sin días registrados para el año de derecho {anio_sel}. "
                 "Cambia de año con las flechas o registra periodos en "
                 "<b>Vacaciones</b>.", "info")
        else:
            fig = px.bar(pl, x="Colaborador", y="Días", color="Concepto",
                         barmode="stack", color_discrete_map=COLOR_CONCEPTO,
                         category_orders={"Concepto": list(COLOR_CONCEPTO)})
            fig.update_traces(marker_line_color=WHITE, marker_line_width=1.3)
            fig.update_xaxes(title=None, tickangle=-12)
            st.plotly_chart(estilo_fig(fig, alto=430, x_grid=False),
                            use_container_width=True)

    with tb[1]:
        chtitle("Ranking de consumo", "La línea punteada marca el 100% del saldo anual")
        d = res.sort_values("% consumido")
        fig = px.bar(d, x="% consumido", y="Colaborador", orientation="h",
                     text="% consumido", color="% consumido",
                     color_continuous_scale=ESCALA_CONTINUA,
                     range_x=[0, max(112, float(d["% consumido"].max() or 0) + 14)])
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                          cliponaxis=False, textfont_color=NAVY)
        fig.update_yaxes(title=None)
        fig.add_vline(x=100, line_dash="dot", line_color=NAVY)
        st.plotly_chart(estilo_fig(fig, leyenda=False, alto=max(260, 54 * len(d)),
                                   y_grid=False).update_layout(coloraxis_showscale=False),
                        use_container_width=True)

    with tb[2]:
        chtitle(f"Días de ausencia por mes — calendario {anio_sel}",
                "Incluye vacaciones, permisos e incapacidades")
        dm = dias_por_mes(emp, vac, fer, anio_sel, pais_f)
        if dm["Días"].sum() == 0:
            nota(f"Sin ausencias registradas durante {anio_sel}.", "info")
        else:
            fig = px.bar(dm, x="Mes", y="Días", color="Estado", barmode="stack",
                         color_discrete_map=COLOR_ESTADO)
            fig.update_traces(marker_line_color=WHITE, marker_line_width=1.2)
            fig.update_xaxes(title=None)
            st.plotly_chart(estilo_fig(fig, alto=400, x_grid=False),
                            use_container_width=True)
            top = dm.groupby("Mes", sort=False)["Días"].sum()
            if top.max() > 0:
                st.caption(f"Mes con mayor carga: {top.idxmax()} "
                           f"({int(top.max())} días hábiles).")

    with tb[3]:
        pp = res.groupby("Pais", as_index=False)[
            ["Días asignados", "Tomados", "Proyectados", "Saldo"]].sum()
        c1, c2 = st.columns(2)
        with c1:
            chtitle("Días asignados por país")
            fig = px.pie(pp, names="Pais", values="Días asignados", hole=.58,
                         color="Pais", color_discrete_map=COLOR_PAIS)
            fig.update_traces(textinfo="label+value", textfont_color=NAVY,
                              marker=dict(line=dict(color=WHITE, width=3)))
            st.plotly_chart(estilo_fig(fig, alto=330), use_container_width=True)
        with c2:
            chtitle("Comparativo de uso por país")
            m = pp.melt(id_vars="Pais", value_vars=["Tomados", "Proyectados", "Saldo"],
                        var_name="Concepto", value_name="Días")
            fig = px.bar(m, x="Pais", y="Días", color="Concepto", barmode="group",
                         color_discrete_map=COLOR_CONCEPTO, text="Días")
            fig.update_traces(textposition="outside", cliponaxis=False,
                              textfont_color=NAVY)
            fig.update_xaxes(title=None)
            st.plotly_chart(estilo_fig(fig, alto=330, x_grid=False),
                            use_container_width=True)
        tabla_marca(pp.rename(columns={"Pais": "País"}))

    with tb[4]:
        chtitle("Días usados agrupados por año de derecho",
                "Permite ver quién arrastra días de ejercicios anteriores")
        pv, largo = pivot_por_anio(emp, vac, fer, pais_f)
        if largo.empty:
            nota("Sin días aprobados o tomados todavía.", "info")
        else:
            fig = px.bar(largo, x="Colaborador", y="Días", color="Año de derecho",
                         barmode="stack", color_discrete_sequence=PALETA_SERIES)
            fig.update_traces(marker_line_color=WHITE, marker_line_width=1.2)
            fig.update_xaxes(title=None, tickangle=-12)
            st.plotly_chart(estilo_fig(fig, alto=400, x_grid=False),
                            use_container_width=True)

    if modo_todos:
        with tb[5]:
            chtitle(f"Comparativo entre equipos — ejercicio {anio_sel}")
            ge = res.groupby("Equipo", as_index=False).agg(
                Personas=("ID", "count"), Asignados=("Días asignados", "sum"),
                Tomados=("Tomados", "sum"), Proyectados=("Proyectados", "sum"),
                Saldo=("Saldo", "sum"))
            ge["% consumido"] = (100 * (ge["Tomados"] + ge["Proyectados"]) /
                                 ge["Asignados"].replace(0, pd.NA)).round(1).fillna(0)
            tabla_marca(ge, pct_cols=["% consumido"])
            m = ge.melt(id_vars="Equipo", value_vars=["Tomados", "Proyectados", "Saldo"],
                        var_name="Concepto", value_name="Días")
            fig = px.bar(m, x="Equipo", y="Días", color="Concepto", barmode="stack",
                         color_discrete_map=COLOR_CONCEPTO)
            fig.update_traces(marker_line_color=WHITE, marker_line_width=1.2)
            fig.update_xaxes(title=None)
            st.plotly_chart(estilo_fig(fig, alto=380, x_grid=False),
                            use_container_width=True)

    sect("Días usados por año de derecho (acumulados)")
    pv, _ = pivot_por_anio(emp, vac, fer, pais_f)
    if pv.empty:
        nota("Aún no hay días de vacaciones aprobados o tomados.", "info")
    else:
        tabla_marca(pv)
        st.caption("Incluye solo periodos Aprobada o Tomada.")

    sect(f"Detalle por persona — año de derecho {anio_sel}")
    c1, c2 = cols([1.3, 2.7], va="bottom")
    orden = c1.selectbox("Ordenar por", ["Colaborador", "Saldo", "% consumido",
                                         "Comprometidos", "Días asignados"],
                         key="db_ord")
    buscar = c2.text_input("Buscar persona", placeholder="Escribe un nombre…",
                           key="db_find")
    det = res.sort_values(orden, ascending=(orden == "Colaborador"))
    if buscar.strip():
        det = det[det["Colaborador"].str.contains(buscar.strip(), case=False, na=False)]
    cols_det = ["ID"] + (["Equipo"] if modo_todos else []) + [
        "Colaborador", "País", "Puesto", "Días asignados", "Tomados", "Proyectados",
        "En solicitud", "Comprometidos", "Saldo", "% consumido", "Otras ausencias",
        "Estatus"]
    tabla_marca(det[cols_det], pct_cols=["% consumido"])

    d1, d2 = st.columns(2)
    d1.download_button(f"Detalle {anio_sel} (CSV)",
                       det[cols_det].to_csv(index=False).encode("utf-8-sig"),
                       f"detalle_{anio_sel}.csv", "text/csv", use_container_width=True)
    if not tras.empty:
        d2.download_button("Días con traslape (CSV)",
                           tras.to_csv(index=False).encode("utf-8-sig"),
                           "dias_con_traslape.csv", "text/csv", use_container_width=True)

    with st.expander("Cobertura · días con 2 o más personas ausentes (próximos 60 días)"):
        if tras.empty:
            nota("No hay traslapes en los próximos 60 días.", "ok")
        else:
            t = tras.copy()
            t["Fecha"] = t["Fecha"].apply(
                lambda d: f'{d:%d/%m/%Y} ({DIAS_ES[d.weekday()]})')
            tabla_marca(t)

# ═══════════════════════════ EQUIPOS ═══════════════════════════
elif seccion == "Equipos":
    page_header("Equipos de la empresa", "Equipos <em>·</em> estructura organizacional",
                "Cada equipo mantiene su información separada · los feriados se "
                "comparten por país", f"{len(equipos)} equipo(s) registrados")

    m = st.columns(4)
    m[0].metric("Equipos", len(equipos))
    m[1].metric("Personas totales", len(emp_all))
    m[2].metric("Periodos totales", len(vac_all))
    m[3].metric("Equipos activos", int(equipos["activo"].sum()))

    sect("Resumen por equipo")
    cards = st.columns(min(3, max(1, len(equipos))))
    for i, (_, r) in enumerate(equipos.iterrows()):
        sub = emp_all[emp_all["equipo_id"] == r["id"]]
        vsub = vac_all[vac_all["empleado_id"].isin(sub["id"])]
        rs = resumen_empleados(sub, vsub, fer, anio_sel, solo_activos=True)
        asg = int(rs["Días asignados"].sum()) if not rs.empty else 0
        comp = int(rs["Comprometidos"].sum()) if not rs.empty else 0
        pc = round(100 * comp / asg, 1) if asg else 0
        with cards[i % len(cards)]:
            st.markdown(
                f'<div class="eqcard" style="border-left-color:{r["color"]}">'
                f'<b>{r["nombre"]}</b>{"" if r["activo"] else " · inactivo"}<br>'
                f'<span>Manager: {r["manager"] or "—"}</span><br>'
                f'<span>{len(sub)} personas · {len(vsub)} periodos</span><br>'
                f'<span>{asg} días asignados {anio_sel} · {pc}% consumido</span>'
                f'{"<br><span>" + r["descripcion"] + "</span>" if r["descripcion"] else ""}'
                f'</div>', unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["Crear equipo", "Editar equipos",
                              "Mover personas", "Eliminar equipo"])

    with t1:
        with st.form("f_eq_new", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nombre del equipo")
            mgr = c2.text_input("Manager")
            desc = st.text_input("Descripción")
            col = st.selectbox("Color identificador (paleta WPP Media)", PALETA_SERIES,
                               index=2, format_func=lambda c: NOMBRE_COLOR.get(c, c))
            if st.form_submit_button("Crear equipo", type="primary"):
                if not nom.strip() or not mgr.strip():
                    flash("Nombre y manager son obligatorios.", "critico")
                elif nom.strip().lower() in [n.lower() for n in eq_nom.values()]:
                    flash("Ya existe un equipo con ese nombre.", "aviso")
                else:
                    base = get_equipos()
                    nid = next_id(base)
                    save_equipos(pd.concat([base, pd.DataFrame([{
                        "id": nid, "nombre": nom.strip(), "manager": mgr.strip(),
                        "descripcion": desc.strip(), "color": col, "activo": True}])],
                        ignore_index=True))
                    st.session_state.scope_eq = str(nid)
                    bump("v_eq")
                    flash(f"Equipo <b>{nom}</b> creado y seleccionado.", "ok")
                st.rerun()

    with t2:
        ed = st.data_editor(
            equipos, use_container_width=True, hide_index=True, num_rows="fixed",
            key=f"ed_eq_{ver('v_eq')}", disabled=["id"],
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "nombre": st.column_config.TextColumn("Equipo", required=True),
                "manager": st.column_config.TextColumn("Manager"),
                "descripcion": st.column_config.TextColumn("Descripción", width="medium"),
                "color": st.column_config.SelectboxColumn("Color", options=PALETA_SERIES,
                                                          width="small"),
                "activo": st.column_config.CheckboxColumn("Activo")})
        if st.button("Guardar equipos", type="primary"):
            save_equipos(ed)
            bump("v_eq")
            flash("Equipos actualizados.", "ok")
            st.rerun()

    with t3:
        if emp_all.empty:
            nota("Aún no hay personas registradas.", "info")
        else:
            etq = {f'#{r["id"]} · {r["nombre"]} ({eq_nom.get(r["equipo_id"],"—")})': r["id"]
                   for _, r in emp_all.iterrows()}
            sel = st.multiselect("Personas a mover", list(etq.keys()))
            dest = st.selectbox("Equipo destino", equipos["nombre"].tolist())
            if st.button("Mover", type="primary", disabled=not sel):
                ids = [etq[s] for s in sel]
                base = get_empleados()
                base.loc[base["id"].isin(ids), "equipo_id"] = nom_eq[dest]
                save_empleados(base)
                bump("v_emp")
                flash(f"{len(ids)} persona(s) movidas a <b>{dest}</b>.", "ok")
                st.rerun()

    with t4:
        if len(equipos) <= 1:
            nota("Debe existir al menos un equipo. Crea otro antes de eliminar este.",
                 "info")
        else:
            victima = st.selectbox("Equipo a eliminar", equipos["nombre"].tolist(),
                                   key="eq_del")
            vid = nom_eq[victima]
            n_per = int((emp_all["equipo_id"] == vid).sum())
            nota(f'El equipo <b>{victima}</b> tiene <b>{n_per} persona(s)</b>.', "aviso")
            modo = st.radio("¿Qué hacer con sus personas?",
                            ["Moverlas a otro equipo", "Eliminarlas junto con sus periodos"])
            destino = None
            if modo.startswith("Mover"):
                destino = st.selectbox("Equipo destino",
                                       [n for n in equipos["nombre"] if n != victima])
            conf = st.checkbox("Confirmo esta acción irreversible")
            if st.button("Eliminar equipo", type="primary", disabled=not conf):
                be, bv, bq = get_empleados(), get_vacaciones(), get_equipos()
                if modo.startswith("Mover"):
                    be.loc[be["equipo_id"] == vid, "equipo_id"] = nom_eq[destino]
                else:
                    ids = be[be["equipo_id"] == vid]["id"].tolist()
                    be = be[be["equipo_id"] != vid]
                    bv = bv[~bv["empleado_id"].isin(ids)]
                    save_csv(bv, F_VACACIONES)
                save_empleados(be)
                save_equipos(bq[bq["id"] != vid])
                st.session_state.scope_eq = str(int(bq[bq["id"] != vid]["id"].min()))
                bump("v_eq"); bump("v_emp"); bump("v_vac")
                flash(f"Equipo <b>{victima}</b> eliminado.", "ok")
                st.rerun()

# ═══════════════════════════ PERSONAS ═══════════════════════════
elif seccion == "Personas":
    page_header("Personas del equipo", "Personas <em>·</em> plantilla del equipo",
                "Sin límite de integrantes · agrega, edita, mueve y elimina", etiqueta_eq)

    if exige_equipo("Para agregar personas, elige el equipo al que pertenecen."):
        with st.expander("Agregar persona", expanded=emp.empty):
            with st.form("f_emp", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                nombre = c1.text_input("Nombre completo")
                pais = c2.selectbox("País", PAISES)
                puesto = c3.text_input("Puesto")
                c4, c5, c6 = st.columns(3)
                email = c4.text_input("Email")
                ingreso = c5.date_input("Fecha de ingreso", value=date.today(),
                                        min_value=date(1980, 1, 1),
                                        max_value=date(2100, 12, 31))
                dias = c6.number_input("Días de vacaciones / año", 0, 365, 12)
                if st.form_submit_button("Guardar persona", type="primary"):
                    if not nombre.strip():
                        flash("El nombre es obligatorio.", "critico")
                    else:
                        df = get_empleados()
                        nuevo = pd.DataFrame([{
                            "id": next_id(df), "equipo_id": equipo_id,
                            "nombre": nombre.strip(), "pais": pais,
                            "puesto": puesto.strip(), "email": email.strip(),
                            "fecha_ingreso": ingreso.isoformat(),
                            "dias_asignados": int(dias), "activo": True}])
                        save_empleados(pd.concat([df, nuevo], ignore_index=True))
                        bump("v_emp")
                        flash(f"<b>{nombre}</b> agregado a {eq_nom.get(equipo_id)}.", "ok")
                    st.rerun()

    if emp.empty:
        nota("Este equipo todavía no tiene personas registradas.", "info")
        st.stop()

    m = st.columns(4)
    m[0].metric("Total", len(emp))
    m[1].metric("Activas", int(emp["activo"].sum()))
    m[2].metric("México (MX)", int((emp["pais"] == "México").sum()))
    m[3].metric("Colombia (CO)", int((emp["pais"] == "Colombia").sum()))

    t1, t2, t3 = st.tabs(["Editar personas", "Acciones rápidas", "Eliminar"])

    with t1:
        base_ed = emp.copy()
        base_ed["Equipo"] = base_ed["equipo_id"].map(eq_nom)
        base_ed = base_ed[["id", "Equipo", "nombre", "pais", "puesto", "email",
                           "fecha_ingreso", "dias_asignados", "activo"]]
        ed = st.data_editor(
            base_ed, use_container_width=True, hide_index=True, num_rows="fixed",
            key=f"ed_emp_{ver('v_emp')}", disabled=["id"],
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "Equipo": st.column_config.SelectboxColumn(
                    "Equipo", options=equipos["nombre"].tolist(), required=True,
                    help="Cambiar aquí mueve a la persona de equipo"),
                "nombre": st.column_config.TextColumn("Nombre", required=True),
                "pais": st.column_config.SelectboxColumn("País", options=PAISES,
                                                         required=True),
                "puesto": st.column_config.TextColumn("Puesto"),
                "email": st.column_config.TextColumn("Email"),
                "fecha_ingreso": st.column_config.TextColumn("Ingreso (YYYY-MM-DD)"),
                "dias_asignados": st.column_config.NumberColumn("Días/año", min_value=0,
                                                                max_value=365),
                "activo": st.column_config.CheckboxColumn(
                    "Activo", help="Solo las activas se suman en el Dashboard")})
        if st.button("Guardar cambios", type="primary", key="sv_emp"):
            nuevo = ed.copy()
            nuevo["equipo_id"] = nuevo["Equipo"].map(nom_eq).fillna(
                equipo_id or 1).astype(int)
            nuevo = nuevo.drop(columns=["Equipo"])
            base = get_empleados()
            otros = base[~base["id"].isin(nuevo["id"])]
            save_empleados(pd.concat([otros, nuevo], ignore_index=True).sort_values("id"))
            bump("v_emp")
            flash("Cambios guardados.", "ok")
            st.rerun()

    with t2:
        c1, c2, c3 = st.columns(3)
        if c1.button("Activar a todas", use_container_width=True):
            base = get_empleados()
            base.loc[base["id"].isin(emp["id"]), "activo"] = True
            save_empleados(base); bump("v_emp"); flash("Personas activadas.", "ok")
            st.rerun()
        if c2.button("Desactivar a todas", use_container_width=True):
            base = get_empleados()
            base.loc[base["id"].isin(emp["id"]), "activo"] = False
            save_empleados(base); bump("v_emp"); flash("Personas desactivadas.", "aviso")
            st.rerun()
        with c3.popover("Asignar días por país", use_container_width=True):
            p_sel = st.selectbox("País", PAISES, key="ap_pais")
            d_sel = st.number_input("Días / año", 0, 365, 12, key="ap_dias")
            if st.button("Aplicar", type="primary", key="ap_go"):
                base = get_empleados()
                mask = base["id"].isin(emp["id"]) & (base["pais"] == p_sel)
                base.loc[mask, "dias_asignados"] = int(d_sel)
                save_empleados(base); bump("v_emp")
                flash(f"{p_sel}: {int(d_sel)} días por persona.", "ok")
                st.rerun()
        st.caption("Las acciones aplican solo a las personas del ámbito actual.")

    with t3:
        nota("Al eliminar una persona se borran <b>todos sus periodos</b> de vacaciones.",
             "aviso")
        etq = {f'#{r["id"]} · {r["nombre"]} ({COD_PAIS.get(r["pais"],"")})': r["id"]
               for _, r in emp.iterrows()}
        sel = st.multiselect("Selecciona a quién eliminar", list(etq.keys()))
        conf = st.checkbox("Confirmo que deseo eliminarlas permanentemente")
        if st.button("Eliminar seleccionadas", type="primary",
                     disabled=not (sel and conf)):
            ids = [etq[s] for s in sel]
            base = get_empleados()
            save_empleados(base[~base["id"].isin(ids)])
            v = get_vacaciones()
            save_csv(v[~v["empleado_id"].isin(ids)], F_VACACIONES)
            bump("v_emp"); bump("v_vac")
            flash(f"Eliminadas: {len(ids)} persona(s).", "ok")
            st.rerun()

# ═══════════════════════════ VACACIONES ═══════════════════════════
elif seccion == "Vacaciones":
    page_header("Registro y proyección de vacaciones",
                "Vacaciones <em>·</em> registro y proyección",
                "Captura individual o por lotes · clasificación por año de derecho",
                etiqueta_eq)

    if emp.empty:
        nota("Este equipo no tiene personas. Agrégalas en <b>Personas</b>.", "aviso")
        st.stop()

    ops = {f'{r["nombre"]} ({COD_PAIS.get(r["pais"],"")})': r["id"]
           for _, r in emp.iterrows()}
    ops_lbl = list(ops.keys())

    tA, tB = st.tabs(["Registro individual", "Registro múltiple"])

    with tA:
        with st.form("f_vac", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            quien = c1.selectbox("Persona", ops_lbl)
            tipo = c2.selectbox("Tipo", TIPOS)
            estado = c3.selectbox("Estado", ESTADOS, index=1)
            anio_der = c4.selectbox("Año de derecho", ANIOS_OPC,
                                    index=ANIOS_OPC.index(anio_sel))
            c5, c6 = st.columns(2)
            f_ini = c5.date_input("Fecha inicio", value=date.today())
            f_fin = c6.date_input("Fecha fin", value=date.today() + timedelta(days=4))
            coment = st.text_input("Comentario")

            eid = ops[quien]
            pe = emp.loc[emp["id"] == eid, "pais"].iloc[0]
            dh = dias_habiles(f_ini, f_fin, fer_dict.get(pe, set()))
            nota(f'<b>{dh} días hábiles</b> · {dias_naturales(f_ini, f_fin)} naturales · '
                 f'saldo <b>{anio_der}</b> · {pe} ({COD_PAIS.get(pe,"")})', "info")

            if st.form_submit_button("Guardar periodo", type="primary"):
                if f_fin < f_ini:
                    flash("La fecha fin no puede ser anterior a la de inicio.", "critico")
                else:
                    df = get_vacaciones()
                    if hay_traslape(df, eid, f_ini, f_fin):
                        flash("Ya existe un periodo que se traslapa con esas fechas.",
                              "critico")
                    else:
                        nuevo = pd.DataFrame([{
                            "id": next_id(df), "empleado_id": eid,
                            "fecha_inicio": f_ini.isoformat(),
                            "fecha_fin": f_fin.isoformat(),
                            "anio_derecho": int(anio_der), "tipo": tipo,
                            "estado": estado, "comentario": coment}])
                        save_csv(pd.concat([df, nuevo], ignore_index=True), F_VACACIONES)
                        bump("v_vac")
                        flash("Periodo registrado.", "ok")
                st.rerun()

    with tB:
        st.caption("Agrega filas con el botón + de la tabla y guarda todo de una vez. "
                   "Puedes mezclar personas y años de derecho.")
        n_ini = 4
        plantilla = pd.DataFrame({
            "Persona": [ops_lbl[0]] * n_ini,
            "Inicio": pd.Series([pd.NaT] * n_ini, dtype="datetime64[ns]"),
            "Fin": pd.Series([pd.NaT] * n_ini, dtype="datetime64[ns]"),
            "Año de derecho": [anio_sel] * n_ini,
            "Tipo": ["Vacaciones"] * n_ini,
            "Estado": ["Aprobada"] * n_ini,
            "Comentario": [""] * n_ini})
        lote = st.data_editor(
            plantilla, use_container_width=True, hide_index=True, num_rows="dynamic",
            key=f"ed_lote_{ver('v_lote')}",
            column_config={
                "Persona": st.column_config.SelectboxColumn(options=ops_lbl,
                                                            required=True),
                "Inicio": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Fin": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Año de derecho": st.column_config.NumberColumn(
                    min_value=2015, max_value=2100, step=1, format="%d"),
                "Tipo": st.column_config.SelectboxColumn(options=TIPOS),
                "Estado": st.column_config.SelectboxColumn(options=ESTADOS),
                "Comentario": st.column_config.TextColumn(width="medium")})

        prev, listos = [], []
        for i, r in lote.iterrows():
            if pd.isna(r["Inicio"]) or pd.isna(r["Fin"]) or not r["Persona"]:
                continue
            ini, fin = pd.to_datetime(r["Inicio"]).date(), pd.to_datetime(r["Fin"]).date()
            eid = ops.get(r["Persona"])
            pe = paises.get(eid, PAISES[0])
            err = "Fin anterior a inicio" if fin < ini else ""
            d = dias_habiles(ini, fin, fer_dict.get(pe, set()))
            prev.append({"Fila": i + 1, "Persona": nombres.get(eid, "?"),
                         "País": COD_PAIS.get(pe, ""),
                         "Inicio": ini.strftime("%d/%m/%Y"),
                         "Fin": fin.strftime("%d/%m/%Y"),
                         "Días hábiles": d, "Año de derecho": int(r["Año de derecho"]),
                         "Tipo": r["Tipo"], "Estado": r["Estado"],
                         "Validación": err or "OK"})
            listos.append({"eid": eid, "ini": ini, "fin": fin,
                           "anio": int(r["Año de derecho"]), "tipo": r["Tipo"],
                           "estado": r["Estado"], "coment": r["Comentario"] or "",
                           "err": err})

        if prev:
            sect("Vista previa del lote")
            dfp = pd.DataFrame(prev)
            tabla_marca(dfp)
            tot = dfp.groupby(["Persona", "Año de derecho"])["Días hábiles"].sum().reset_index()
            st.caption("Totales por persona y año de derecho:")
            tabla_marca(tot)
            if st.button(f"Guardar {len(listos)} periodo(s)", type="primary",
                         key="sv_lote"):
                base = get_vacaciones()
                nid = next_id(base)
                nuevos, errores, pend = [], [], []
                for k2, it in enumerate(listos, start=1):
                    if it["err"]:
                        errores.append(f"Fila {k2}: {it['err']}"); continue
                    if hay_traslape(base, it["eid"], it["ini"], it["fin"]):
                        errores.append(f"Fila {k2}: se traslapa con un periodo ya "
                                       f"registrado")
                        continue
                    if any(p["eid"] == it["eid"] and p["ini"] <= it["fin"]
                           and p["fin"] >= it["ini"] for p in pend):
                        errores.append(f"Fila {k2}: se traslapa con otra fila del lote")
                        continue
                    pend.append(it)
                    nuevos.append({"id": nid, "empleado_id": it["eid"],
                                   "fecha_inicio": it["ini"].isoformat(),
                                   "fecha_fin": it["fin"].isoformat(),
                                   "anio_derecho": it["anio"], "tipo": it["tipo"],
                                   "estado": it["estado"], "comentario": it["coment"]})
                    nid += 1
                if nuevos:
                    save_csv(pd.concat([base, pd.DataFrame(nuevos)], ignore_index=True),
                             F_VACACIONES)
                    bump("v_vac"); bump("v_lote")
                    flash(f"Se guardaron {len(nuevos)} periodo(s).", "ok")
                for e in errores:
                    flash(e, "critico")
                st.rerun()
        else:
            nota("Completa al menos una fila con <b>Inicio</b> y <b>Fin</b>.", "info")

    st.divider()
    if vac.empty:
        nota("Sin periodos registrados en este ámbito.", "info")
        st.stop()

    tabla = vac.copy()
    tabla["Persona"] = tabla["empleado_id"].map(nombres).fillna("(eliminada)")
    tabla["Equipo"] = tabla["empleado_id"].map(emp_eq).map(eq_nom).fillna("—")
    tabla["País"] = tabla["empleado_id"].map(paises).map(COD_PAIS).fillna("")
    tabla["Días hábiles"] = tabla.apply(lambda r: dh_de_fila(r, paises, fer_dict), axis=1)
    tabla["Días naturales"] = tabla.apply(
        lambda r: dias_naturales(r["fecha_inicio"], r["fecha_fin"]), axis=1)

    t1, t2, t3 = st.tabs(["Periodos registrados", "Eliminar periodos", "Proyección"])

    with t1:
        c1, c2, c3, c4 = st.columns(4)
        f1 = c1.multiselect("Persona", sorted(set(tabla["Persona"])))
        f2 = c2.multiselect("Estado", ESTADOS)
        f3 = c3.multiselect("País", list(COD_PAIS.values()))
        f4 = c4.multiselect("Año de derecho", sorted(set(tabla["anio_derecho"].tolist())))
        t = tabla.copy()
        if f1: t = t[t["Persona"].isin(f1)]
        if f2: t = t[t["estado"].isin(f2)]
        if f3: t = t[t["País"].isin(f3)]
        if f4: t = t[t["anio_derecho"].isin(f4)]

        base_cols = ["id", "empleado_id", "Equipo", "Persona", "País", "fecha_inicio",
                     "fecha_fin", "Días hábiles", "Días naturales", "anio_derecho",
                     "tipo", "estado", "comentario"]
        vista = (t[base_cols].sort_values("fecha_inicio", ascending=False)
                 .rename(columns={"id": "ID", "empleado_id": "ID Empleado",
                                  "fecha_inicio": "Inicio", "fecha_fin": "Fin",
                                  "anio_derecho": "Año de derecho", "tipo": "Tipo",
                                  "estado": "Estado", "comentario": "Comentario"}))
        ed = st.data_editor(
            vista, use_container_width=True, hide_index=True, num_rows="fixed",
            key=f"ed_vac_{ver('v_vac')}",
            disabled=["ID", "ID Empleado", "Equipo", "Persona", "País", "Días hábiles",
                      "Días naturales"],
            column_config={
                "Inicio": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Fin": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Año de derecho": st.column_config.NumberColumn(
                    min_value=2015, max_value=2100, step=1, format="%d"),
                "Tipo": st.column_config.SelectboxColumn(options=TIPOS),
                "Estado": st.column_config.SelectboxColumn(options=ESTADOS),
                "Comentario": st.column_config.TextColumn()})

        cc1, cc2 = st.columns([1, 2])
        if cc1.button("Guardar cambios", type="primary", key="sv_vac"):
            base = get_vacaciones()
            for _, r in ed.iterrows():
                i = base.index[base["id"] == r["ID"]]
                if len(i):
                    base.loc[i, "fecha_inicio"] = pd.to_datetime(
                        r["Inicio"]).date().isoformat()
                    base.loc[i, "fecha_fin"] = pd.to_datetime(r["Fin"]).date().isoformat()
                    base.loc[i, "anio_derecho"] = int(r["Año de derecho"])
                    base.loc[i, "tipo"] = r["Tipo"]
                    base.loc[i, "estado"] = r["Estado"]
                    base.loc[i, "comentario"] = r["Comentario"]
            save_csv(base, F_VACACIONES)
            bump("v_vac")
            flash("Cambios guardados.", "ok")
            st.rerun()

        exp = vista[["ID", "ID Empleado", "Equipo", "Persona", "País", "Inicio", "Fin",
                     "Días hábiles", "Días naturales", "Año de derecho", "Tipo",
                     "Estado", "Comentario"]]
        cc2.download_button("Descargar periodos (CSV)",
                            exp.to_csv(index=False).encode("utf-8-sig"),
                            f"periodos_vacaciones_{date.today():%Y%m%d}.csv", "text/csv",
                            use_container_width=True)

    with t2:
        etq = {f'#{r["id"]} · {r["Persona"]} · {r["fecha_inicio"]:%d/%m/%Y} a '
               f'{r["fecha_fin"]:%d/%m/%Y} · año {int(r["anio_derecho"])} '
               f'({r["estado"]})': r["id"]
               for _, r in tabla.sort_values("fecha_inicio", ascending=False).iterrows()}
        sel = st.multiselect("Selecciona los periodos a eliminar", list(etq.keys()))
        conf = st.checkbox("Confirmo la eliminación", key="cf_vac")
        if st.button("Eliminar periodos", type="primary", disabled=not (sel and conf)):
            ids = [etq[s] for s in sel]
            base = get_vacaciones()
            save_csv(base[~base["id"].isin(ids)], F_VACACIONES)
            bump("v_vac")
            flash(f"Eliminados: {len(ids)} periodo(s).", "ok")
            st.rerun()

    with t3:
        sect(f"Saldos del año de derecho {anio_sel}")
        res = resumen_empleados(emp, vac, fer, anio_sel, eq_nom=eq_nom)
        cols_p = ["ID"] + (["Equipo"] if modo_todos else []) + [
            "Colaborador", "País", "Días asignados", "Tomados", "Proyectados",
            "En solicitud", "Comprometidos", "Saldo", "% consumido", "Estatus"]
        tabla_marca(res[cols_p], pct_cols=["% consumido"])
        st.download_button("Descargar proyección (CSV)",
                           res[cols_p].to_csv(index=False).encode("utf-8-sig"),
                           f"proyeccion_{anio_sel}.csv", "text/csv")
        sect("Días usados por año de derecho")
        pv, _ = pivot_por_anio(emp, vac, fer)
        if pv.empty:
            nota("Sin días aprobados o tomados todavía.", "info")
        else:
            tabla_marca(pv)
            st.download_button("Acumulado por año (CSV)",
                               pv.to_csv(index=False).encode("utf-8-sig"),
                               "dias_por_anio_derecho.csv", "text/csv")

# ═══════════════════════════ CALENDARIO ═══════════════════════════
elif seccion == "Calendario":
    page_header("Calendario del equipo", "Calendario <em>·</em> vista mensual y anual",
                "Navega mes a mes y revisa la línea de tiempo del año", etiqueta_eq)

    if emp.empty:
        nota("Este equipo no tiene personas registradas.", "aviso")
        st.stop()

    st.session_state.setdefault("cal_m", date.today().month)
    st.session_state.setdefault("cal_y", date.today().year)

    def mover(delta):
        m = st.session_state.cal_m + delta
        y = st.session_state.cal_y
        while m < 1:
            m += 12; y -= 1
        while m > 12:
            m -= 12; y += 1
        st.session_state.cal_m, st.session_state.cal_y = m, y

    def ir_hoy():
        st.session_state.cal_m = date.today().month
        st.session_state.cal_y = date.today().year

    n1, n2, n3, n4, n5, n6 = cols([0.7, 0.7, 2.6, 0.7, 0.7, 1.2])
    n1.button("◀◀", help="Año anterior", on_click=mover, args=(-12,),
              use_container_width=True)
    n2.button("◀", help="Mes anterior", on_click=mover, args=(-1,),
              use_container_width=True)
    n3.markdown(f'<div class="navtitle">{MESES_ES[st.session_state.cal_m-1]} '
                f'{st.session_state.cal_y}<small>NAVEGACIÓN RÁPIDA</small></div>',
                unsafe_allow_html=True)
    n4.button("▶", help="Mes siguiente", on_click=mover, args=(1,),
              use_container_width=True)
    n5.button("▶▶", help="Año siguiente", on_click=mover, args=(12,),
              use_container_width=True)
    n6.button("Hoy", on_click=ir_hoy, use_container_width=True)

    k = f'{st.session_state.cal_y}_{st.session_state.cal_m}'
    with st.expander("Ir a un mes específico y filtros"):
        c1, c2 = st.columns(2)
        m_sel = c1.selectbox("Mes", range(1, 13), index=st.session_state.cal_m - 1,
                             format_func=lambda m: MESES_ES[m - 1], key=f"sm_{k}")
        y_sel = c2.number_input("Año", 2015, 2100, st.session_state.cal_y, step=1,
                                key=f"sy_{k}")
        if m_sel != st.session_state.cal_m or int(y_sel) != st.session_state.cal_y:
            st.session_state.cal_m, st.session_state.cal_y = m_sel, int(y_sel)
            st.rerun()
        c3, c4, c5 = st.columns([1, 1.4, 1])
        c3.multiselect("País", PAISES, default=PAISES, key=f"pf_{k}")
        c4.multiselect("Estados", ESTADOS, default=["Solicitada", "Aprobada", "Tomada"],
                       key=f"ef_{k}")
        c5.multiselect("Año de derecho",
                       sorted(set(vac["anio_derecho"].tolist())) if not vac.empty else [],
                       key=f"af_{k}")
        st.checkbox("Mostrar año de derecho en cada etiqueta", value=True, key=f"ma_{k}")

    pf = st.session_state.get(f"pf_{k}", PAISES) or PAISES
    ef = st.session_state.get(f"ef_{k}", ["Solicitada", "Aprobada", "Tomada"])
    af = st.session_state.get(f"af_{k}", [])
    mostrar_anio = st.session_state.get(f"ma_{k}", True)

    vf = vac[vac["estado"].isin(ef)] if not vac.empty else vac
    if af and not vf.empty:
        vf = vf[vf["anio_derecho"].isin(af)]

    st.markdown(CAL_CSS + leyenda(ef), unsafe_allow_html=True)
    mapa = expandir_dias(vf, emp, cmap) if not vf.empty else {}
    render_calendario(st.session_state.cal_y, st.session_state.cal_m, mapa, fer_dict, pf,
                      mostrar_anio)

    ini_mes = date(st.session_state.cal_y, st.session_state.cal_m, 1)
    fin_mes = date(st.session_state.cal_y, st.session_state.cal_m,
                   calendar.monthrange(st.session_state.cal_y, st.session_state.cal_m)[1])
    if not vf.empty:
        en_mes = vf[(vf["fecha_inicio"] <= fin_mes) & (vf["fecha_fin"] >= ini_mes)]
        c = st.columns(3)
        c[0].metric("Personas con ausencia", en_mes["empleado_id"].nunique())
        c[1].metric("Periodos en el mes", len(en_mes))
        c[2].metric("Feriados del mes",
                    sum(1 for p in pf for f in fer_dict.get(p, set())
                        if ini_mes <= f <= fin_mes))

    chtitle("Línea de tiempo anual", f"Año {st.session_state.cal_y}")
    if vf.empty:
        nota("Sin periodos para graficar.", "info")
    else:
        g = vf.copy()
        g["Persona"] = g["empleado_id"].map(nombres)
        g["País"] = g["empleado_id"].map(paises)
        g = g.dropna(subset=["Persona"])
        g = g[g["País"].isin(pf)]
        g = g[(pd.to_datetime(g["fecha_inicio"]).dt.year <= st.session_state.cal_y) &
              (pd.to_datetime(g["fecha_fin"]).dt.year >= st.session_state.cal_y)]
        if g.empty:
            nota("Sin periodos en el año seleccionado.", "info")
        else:
            g["Inicio"] = pd.to_datetime(g["fecha_inicio"])
            g["Fin"] = pd.to_datetime(g["fecha_fin"]) + pd.Timedelta(days=1)
            g["Año derecho"] = g["anio_derecho"].astype(str)
            fig = px.timeline(g, x_start="Inicio", x_end="Fin", y="Persona",
                              color="estado",
                              hover_data=["tipo", "Año derecho", "comentario", "País"],
                              color_discrete_map=COLOR_ESTADO)
            fig.update_yaxes(autorange="reversed", title=None)
            fig.update_xaxes(range=[f"{st.session_state.cal_y}-01-01",
                                    f"{st.session_state.cal_y}-12-31"])
            fig.add_vline(x=datetime.now(), line_dash="dash", line_color=NAVY)
            fig.update_traces(marker_line_color=WHITE, marker_line_width=1.3)
            st.plotly_chart(estilo_fig(fig, alto=130 + 34 * g["Persona"].nunique()),
                            use_container_width=True)

# ═══════════════════════════ FERIADOS ═══════════════════════════
elif seccion in ("Feriados México", "Feriados Colombia"):
    pais = "México" if "México" in seccion else "Colombia"
    cpais = FERIADO_COLOR[pais]
    page_header(f"Días feriados · {pais}",
                f"Feriados <em>·</em> {pais} ({COD_PAIS[pais]})",
                "Son por país y aplican a <b>todos los equipos</b> · "
                "IDs consecutivos y cronológicos", "Catálogo compartido")

    st.markdown(f'<div class="card" style="border-left:5px solid {cpais};'
                f'background:{FERIADO_BG[pais]}">'
                f'<b>Color en el calendario:</b> '
                f'<span class="pill" style="background:{cpais};color:{NAVY}">'
                f'{NOMBRE_COLOR[cpais]}</span> &nbsp;·&nbsp; '
                f'<span style="font-size:.85rem">Los IDs se reordenan por fecha al '
                f'agregar o eliminar.</span></div>', unsafe_allow_html=True)

    c1, c2 = cols([2, 1], va="bottom")
    with c1:
        with st.form(f"f_fer_{pais}", clear_on_submit=True):
            a, b = st.columns([1, 2])
            f = a.date_input("Fecha", value=date(anio_sel, 1, 1))
            desc = b.text_input("Descripción", placeholder="Ej. Día de la Independencia")
            if st.form_submit_button("Agregar feriado", type="primary"):
                df = get_feriados()
                if not df.empty and ((df["pais"] == pais) & (df["fecha"] == f)).any():
                    flash("Ese feriado ya existe.", "aviso")
                else:
                    nuevo = pd.DataFrame([{"id": 0, "pais": pais, "fecha": f.isoformat(),
                                           "descripcion": desc.strip() or "Feriado"}])
                    save_feriados(pd.concat([df, nuevo], ignore_index=True))
                    bump("v_fer")
                    flash("Feriado agregado y IDs reordenados.", "ok")
                st.rerun()
    with c2:
        if st.button(f"Cargar oficiales {anio_sel}", use_container_width=True):
            base = get_feriados()
            oficiales = sorted(feriados_mexico(anio_sel) if pais == "México"
                               else feriados_colombia(anio_sel))
            exist = set(base[base["pais"] == pais]["fecha"]) if not base.empty else set()
            nuevos = [{"id": 0, "pais": pais, "fecha": d.isoformat(), "descripcion": n}
                      for d, n in oficiales if d not in exist]
            if nuevos:
                save_feriados(pd.concat([base, pd.DataFrame(nuevos)], ignore_index=True))
                bump("v_fer")
                flash(f"Agregados {len(nuevos)} feriados de {pais} {anio_sel}.", "ok")
            else:
                flash("Ya están todos cargados.", "info")
            st.rerun()

    fp = fer[fer["pais"] == pais].copy()
    if not fp.empty:
        fp = fp[pd.to_datetime(fp["fecha"]).dt.year == anio_sel]
    if fp.empty:
        nota(f"No hay feriados de {pais} en {anio_sel}. Usa <b>Cargar oficiales</b>.",
             "info")
        st.stop()

    m1, m2, m3 = st.columns(3)
    m1.metric(f"Total {anio_sel}", len(fp))
    m2.metric("En día hábil", int(sum(1 for d in fp["fecha"] if d.weekday() < 5)))
    m3.metric("En fin de semana", int(sum(1 for d in fp["fecha"] if d.weekday() >= 5)))

    t1, t2 = st.tabs(["Editar", "Eliminar"])
    with t1:
        fp = fp.sort_values("fecha").reset_index(drop=True)
        fp["No."] = range(1, len(fp) + 1)
        fp["Día"] = fp["fecha"].apply(lambda d: DIAS_ES[d.weekday()])
        fp["Mes"] = fp["fecha"].apply(lambda d: MESES_ES[d.month - 1])
        vista = (fp[["No.", "id", "fecha", "Día", "Mes", "descripcion"]]
                 .rename(columns={"id": "ID", "fecha": "Fecha",
                                  "descripcion": "Descripción"}))
        ed = st.data_editor(vista, use_container_width=True, hide_index=True,
                            num_rows="fixed", key=f"ed_fer_{pais}_{ver('v_fer')}",
                            disabled=["No.", "ID", "Día", "Mes"],
                            column_config={
                                "No.": st.column_config.NumberColumn(width="small"),
                                "ID": st.column_config.NumberColumn(width="small"),
                                "Fecha": st.column_config.DateColumn(format="DD/MM/YYYY"),
                                "Descripción": st.column_config.TextColumn()})
        if st.button("Guardar feriados", type="primary", key=f"sv_fer_{pais}"):
            base = get_feriados()
            for _, r in ed.iterrows():
                i = base.index[base["id"] == r["ID"]]
                if len(i):
                    base.loc[i, "fecha"] = pd.to_datetime(r["Fecha"]).date().isoformat()
                    base.loc[i, "descripcion"] = r["Descripción"]
            save_feriados(base)
            bump("v_fer")
            flash("Feriados actualizados y renumerados.", "ok")
            st.rerun()

    with t2:
        etq = {f'#{r["id"]} · {r["fecha"]:%d/%m/%Y} — {r["descripcion"]}': r["id"]
               for _, r in fp.sort_values("fecha").iterrows()}
        sel = st.multiselect("Selecciona los feriados a eliminar", list(etq.keys()))
        conf = st.checkbox("Confirmo la eliminación", key=f"cf_fer_{pais}")
        cA, cB = st.columns(2)
        if cA.button("Eliminar seleccionados", type="primary",
                     disabled=not (sel and conf)):
            ids = [etq[s] for s in sel]
            base = get_feriados()
            save_feriados(base[~base["id"].isin(ids)])
            bump("v_fer")
            flash(f"Eliminados: {len(ids)} feriado(s).", "ok")
            st.rerun()
        if cB.button(f"Borrar todos los de {pais} {anio_sel}", disabled=not conf):
            base = get_feriados()
            mask = ((base["pais"] == pais) &
                    (pd.to_datetime(base["fecha"]).dt.year == anio_sel))
            save_feriados(base[~mask])
            bump("v_fer")
            flash("Feriados del año eliminados.", "ok")
            st.rerun()

# ═══════════════════════════ DATOS ═══════════════════════════
else:
    page_header("Respaldo e importación de datos",
                "Datos <em>·</em> respaldo, auditoría e importación",
                "Descarga, exporta a Excel, audita la identidad visual o restaura",
                etiqueta_eq)

    d = st.columns(4)
    d[0].metric("Equipos", len(equipos))
    d[1].metric("Personas", len(emp_all))
    d[2].metric("Periodos", len(vac_all))
    d[3].metric("Feriados", len(fer))

    sect("Auditoría de identidad visual")
    _, fuentes = font_faces()
    aud = auditar_colores()

    b1, b2 = st.columns([1, 1])
    with b1:
        st.markdown("**Logo**")
        if LOGO:
            nota(f"Detectado: <code>{LOGO}</code><br>Se usa el archivo original, sin "
                 f"recortes ni reescalados.", "ok")
            st.image(LOGO, width=340)
        else:
            nota("No se encontró el logo. Guárdalo como "
                 "<code>assets/WPP Media_Wordmark_Navy_RGB.png</code>.", "critico")

        st.markdown("**Tipografía**")
        if len(fuentes) == 3:
            nota("Tipografía WPP completa: " +
                 ", ".join(f"<code>{f}</code>" for f in fuentes), "ok")
        elif fuentes:
            nota("Tipografía WPP parcial (" + ", ".join(fuentes) +
                 "). Faltan variantes en <code>static/fonts/</code>.", "aviso")
        else:
            nota("No se encontraron las fuentes. Coloca <code>WPP-Regular.woff2</code>, "
                 "<code>WPP-Medium.woff2</code> y <code>WPP-Bold.woff2</code> en "
                 "<code>static/fonts/</code>.", "critico")

    with b2:
        st.markdown("**Tema de Streamlit (config.toml)**")
        if CFG["existe"] and CFG["primary"] and CFG["font"] and CFG["secundario"]:
            nota("Tema correcto. Los elementos nativos usan exclusivamente la paleta "
                 "corporativa.", "ok")
        else:
            det = []
            if not CFG["existe"]:
                det.append("el archivo no existe")
            else:
                if not CFG["primary"]:
                    det.append(f"<b>primaryColor</b> no es <code>{NAVY}</code>")
                if not CFG["font"]:
                    det.append("<b>font</b> no es <code>WPP</code>")
                if not CFG["secundario"]:
                    det.append("contiene colores fuera de la paleta")
            nota("Problemas en <code>.streamlit/config.toml</code>: " + "; ".join(det) +
                 ".", "critico")
        if st.button("Escribir config.toml corporativo", type="primary",
                     use_container_width=True):
            os.makedirs(".streamlit", exist_ok=True)
            with open(os.path.join(".streamlit", "config.toml"), "w",
                      encoding="utf-8") as fh:
                fh.write(CONFIG_TOML)
            st.cache_data.clear()
            flash("Archivo escrito. <b>Detén la app (Ctrl+C) y vuelve a ejecutarla</b>: "
                  "Streamlit lee el tema solo al arrancar.", "ok")
            st.rerun()

        st.markdown("**Escaneo automático del código fuente**")
        if aud is None:
            nota("No se pudo leer el archivo fuente para auditarlo.", "aviso")
        else:
            problemas = bool(aud["hex"]) or bool(aud["nombres"]) or aud["hsl"] or \
                aud["rgb"]
            if not problemas:
                nota(f"Sin colores ajenos a la paleta. Se detectaron "
                     f"<b>{aud['rgba_marca']}</b> usos de <code>rgba()</code>, todos "
                     f"derivados de los hex corporativos.", "ok")
            else:
                if aud["hex"]:
                    nota("Hex fuera de la paleta: " +
                         ", ".join(f"<code>#{h}</code> ({n})"
                                   for h, n in aud["hex"].items()), "critico")
                if aud["nombres"]:
                    nota("Nombres de color prohibidos: " +
                         ", ".join(f"<code>{k}</code> ({v})"
                                   for k, v in aud["nombres"].items()), "critico")
                if aud["hsl"] or aud["rgb"]:
                    nota(f"Usos de <code>hsl()</code>: {aud['hsl']} · "
                         f"<code>rgb()</code> crudo: {aud['rgb']}.", "aviso")

    st.markdown("**Paleta activa**")
    st.markdown(
        '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px">' +
        "".join(f'<span class="sw"><i style="background:{c};'
                f'border:1px solid {LINE}"></i>{NOMBRE_COLOR[c]} {c}</span>'
                for c in PALETA_OFICIAL) + '</div>', unsafe_allow_html=True)
    st.caption("Únicamente estos 7 colores y sus tintes rgba(). El brand book define "
               "White y WPP Navy como los dos neutros, por lo que todos los grises de "
               "la interfaz son transparencias de WPP Navy.")

    solo_eq = st.toggle("Exportar solo el equipo seleccionado", value=not modo_todos,
                        disabled=modo_todos)
    e_exp = (emp if solo_eq else emp_all).copy()
    v_exp = (vac if solo_eq else vac_all).copy()
    e_exp.insert(2, "equipo_nombre", e_exp["equipo_id"].map(eq_nom))
    if not v_exp.empty:
        v_exp.insert(2, "nombre_empleado",
                     v_exp["empleado_id"].map(nombres).fillna("(eliminado)"))
        v_exp.insert(3, "equipo", v_exp["empleado_id"].map(emp_eq).map(eq_nom))

    sect("Descargar respaldos")
    c = st.columns(4)
    c[0].download_button("equipos.csv", equipos.to_csv(index=False).encode("utf-8-sig"),
                         "equipos.csv", "text/csv", use_container_width=True)
    c[1].download_button("empleados.csv", e_exp.to_csv(index=False).encode("utf-8-sig"),
                         "empleados.csv", "text/csv", use_container_width=True)
    c[2].download_button("vacaciones.csv", v_exp.to_csv(index=False).encode("utf-8-sig"),
                         "vacaciones.csv", "text/csv", use_container_width=True)
    c[3].download_button("feriados.csv", fer.to_csv(index=False).encode("utf-8-sig"),
                         "feriados.csv", "text/csv", use_container_width=True)
    st.caption("Vacaciones incluye nombre_empleado y equipo; feriados no lo requiere.")

    sect("Exportar a Excel")
    try:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as xl:
            equipos.to_excel(xl, sheet_name="Equipos", index=False)
            e_exp.to_excel(xl, sheet_name="Personas", index=False)
            v_exp.to_excel(xl, sheet_name="Vacaciones", index=False)
            fer.to_excel(xl, sheet_name="Feriados", index=False)
            for _, q in equipos.iterrows():
                sub = emp_all[emp_all["equipo_id"] == q["id"]]
                if sub.empty:
                    continue
                vs = vac_all[vac_all["empleado_id"].isin(sub["id"])]
                hoja = str(q["nombre"])[:24] or f'Eq{q["id"]}'
                resumen_empleados(sub, vs, fer, anio_sel).drop(columns=["Pais"]).to_excel(
                    xl, sheet_name=f"{hoja} {anio_sel}"[:31], index=False)
        st.download_button("control_vacaciones.xlsx", buf.getvalue(),
                           f"WPPMedia_control_vacaciones_{date.today():%Y%m%d}.xlsx",
                           "application/vnd.openxmlformats-officedocument."
                           "spreadsheetml.sheet", use_container_width=True)
    except Exception as e:
        nota(f"No se pudo generar el Excel ({e}). Verifica <code>openpyxl</code>.",
             "aviso")

    sect("Importar")
    destino = st.selectbox("Archivo destino",
                           ["equipos", "empleados", "vacaciones", "feriados"])
    up = st.file_uploader("Sube un CSV con la misma estructura", type="csv")
    if up is not None:
        prev = pd.read_csv(up, dtype=str, keep_default_na=False)
        tabla_marca(prev.head(10))
        if st.button("Reemplazar datos", type="primary"):
            prev = prev.drop(columns=[c for c in ["equipo_nombre", "nombre_empleado",
                                                  "equipo"] if c in prev.columns])
            if destino == "feriados":
                save_feriados(prev)
            elif destino == "empleados":
                for c in COLS_EMPLEADOS:
                    if c not in prev.columns:
                        prev[c] = ""
                save_empleados(prev)
            elif destino == "equipos":
                for c in COLS_EQUIPOS:
                    if c not in prev.columns:
                        prev[c] = ""
                save_equipos(prev)
            else:
                save_csv(prev, F_VACACIONES)
            bump("v_eq"); bump("v_emp"); bump("v_vac"); bump("v_fer")
            flash(f"Datos de {destino} reemplazados.", "ok")
            st.rerun()

    sect("Mantenimiento")
    c1, c2, c3 = st.columns(3)
    if c1.button("Renumerar feriados", use_container_width=True):
        save_feriados(get_feriados()); bump("v_fer"); flash("Feriados renumerados.", "ok")
        st.rerun()
    if c2.button("Normalizar personas", use_container_width=True):
        save_empleados(get_empleados()); bump("v_emp")
        flash("Personas normalizadas.", "ok"); st.rerun()
    if c3.button("Reasignar huérfanos al 1er equipo", use_container_width=True):
        migrar_a_equipos(); bump("v_emp"); flash("Reasignación completada.", "ok")
        st.rerun()

    sect("Zona peligrosa")
    with st.expander("Borrar datos"):
        modo_borrar = st.radio("Alcance", ["Solo el equipo seleccionado",
                                           "TODO el sistema"])
        if st.checkbox("Confirmo la eliminación"):
            if st.button("Borrar", type="primary"):
                if modo_borrar.startswith("Solo") and not modo_todos:
                    be, bv = get_empleados(), get_vacaciones()
                    ids = be[be["equipo_id"] == equipo_id]["id"].tolist()
                    save_empleados(be[be["equipo_id"] != equipo_id])
                    save_csv(bv[~bv["empleado_id"].isin(ids)], F_VACACIONES)
                    flash(f"Datos de «{eq_nom.get(equipo_id)}» eliminados.", "ok")
                else:
                    for p, cc in [(F_EQUIPOS, COLS_EQUIPOS),
                                  (F_EMPLEADOS, COLS_EMPLEADOS),
                                  (F_VACACIONES, COLS_VACACIONES),
                                  (F_FERIADOS, COLS_FERIADOS)]:
                        save_csv(pd.DataFrame(columns=cc), p)
                    migrar_a_equipos()
                    flash("Sistema reiniciado.", "ok")
                bump("v_eq"); bump("v_emp"); bump("v_vac"); bump("v_fer")
                st.rerun()