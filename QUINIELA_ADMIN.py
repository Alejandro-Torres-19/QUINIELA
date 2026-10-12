import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components
import re
from datetime import datetime, date
import unicodedata

# --- 1. CONFIGURACIÓN INICIAL PÁGINA ---
st.set_page_config(
    page_title="QUINIELA LIGA MX - ADMIN",
    page_icon="⚽",
    layout="wide",
)

# --- ESTILOS CSS VIBRANTES Y MODERNOS (TIPO DASHBOARD DEPORTIVO) ---
st.markdown("""
    <style>
        /* Fondo general de la aplicación */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            color: #f8fafc;
        }

        /* Expandir el ancho de la barra lateral y darle color llamativo */
        [data-testid="stSidebar"] {
            min-width: 320px !important;
            max-width: 320px !important;
            background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%) !important;
            border-right: 2px solid rgba(99, 102, 241, 0.3);
        }

        /* Estilo de pestañas (Tabs) grandes, coloridas y con efecto glow */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(30, 27, 75, 0.5);
            padding: 10px;
            border-radius: 16px;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }

        .stTabs [data-baseweb="tab"] {
            background-color: rgba(15, 23, 42, 0.6);
            border-radius: 10px;
            padding: 12px 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
            border-color: #a855f7;
        }

        .stTabs [data-baseweb="tab"] p {
            font-size: 1.15rem !important;
            font-weight: 800 !important;
            color: #ffffff !important;
        }

        /* Botones principales llamativos con degradado */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%) !important;
            color: white !important;
            font-size: 1.15rem !important;
            font-weight: 800 !important;
            padding: 0.75rem 1.5rem !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            transition: all 0.3s ease;
        }

        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #4f46e5 0%, #db2777 100%) !important;
            box-shadow: 0 6px 20px rgba(236, 72, 153, 0.6);
            transform: translateY(-2px);
        }

        /* Selectboxes e Inputs personalizados */
        .stSelectbox div[data-baseweb="select"], .stTextInput input {
            background-color: rgba(30, 41, 59, 0.7) !important;
            border-radius: 10px !important;
            border: 1.5px solid rgba(99, 102, 241, 0.4) !important;
            color: #ffffff !important;
        }

        /* Encabezados y títulos con efecto brillante */
        h2, h3 {
            font-weight: 900 !important;
            letter-spacing: 0.5px;
            text-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
        }
    </style>
""", unsafe_allow_html=True)


# --- FUNCIÓN DE NORMALIZACIÓN DE TEXTO ---
def normalizar_texto(texto):
    if not texto:
        return ""
    texto_str = str(texto).strip().upper()
    nfkd_form = unicodedata.normalize('NFKD', texto_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


# --- 2. CONEXIÓN Y CARGA CON CACHÉ ---
@st.cache_resource
def conectar_google_sheets():
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key("1T2yrRCQgIM-GjrgGEf3UVrFsS2SltJysv-bZZv6GbaU")
        return spreadsheet
    except Exception as e:
        st.error(f"Error crítico en conexión Google Sheets: {e}")
        return None


@st.cache_data(ttl=600)
def obtener_datos_jornada_cache(jornada_nombre):
    spreadsheet = conectar_google_sheets()
    if not spreadsheet:
        return []
    try:
        sheet_j = spreadsheet.worksheet(jornada_nombre)
        return sheet_j.get_all_values()
    except Exception:
        return []


spreadsheet = conectar_google_sheets()

# --- CALENDARIO Y PARTIDOS OFICIALES ---
CALENDARIO_JORNADAS = {
    "J1": (date(2026, 7, 16), date(2026, 7, 18)),
    "J2": (date(2026, 7, 21), date(2026, 7, 26)),
    "J3": (date(2026, 7, 31), date(2026, 8, 2)),
    "J4": (date(2026, 8, 15), date(2026, 8, 17)),
    "J5": (date(2026, 8, 21), date(2026, 8, 23)),
    "J6": (date(2026, 8, 28), date(2026, 8, 30)),
    "J7": (date(2026, 9, 4), date(2026, 9, 6)),
    "J8": (date(2026, 9, 11), date(2026, 9, 13)),
    "J9": (date(2026, 9, 18), date(2026, 9, 20)),
    "J10": (date(2026, 9, 25), date(2026, 9, 27)),
    "J11": (date(2026, 10, 9), date(2026, 10, 11)),
    "J12": (date(2026, 10, 16), date(2026, 10, 18)),
    "J13": (date(2026, 10, 20), date(2026, 10, 21)),
    "J14": (date(2026, 10, 23), date(2026, 10, 25)),
    "J15": (date(2026, 10, 30), date(2026, 11, 1)),
    "J16": (date(2026, 11, 6), date(2026, 11, 8)),
    "J17": (date(2026, 11, 20), date(2026, 11, 22)),
}

PARTIDOS_OFICIALES_APERTURA_2026 = {
    "J1": [
        ("JUÁREZ", "PUEBLA"), ("PUMAS", "PACHUCA"), ("CHIVAS", "TOLUCA"),
        ("MONTERREY", "SANTOS"), ("AMÉRICA", "ATLANTE"), ("XOLOS", "LEÓN"),
        ("ATLAS", "QUERÉTARO"), ("TIGRES", "CRUZ AZUL"), ("SAN LUIS", "NECAXA")
    ],
    "J2": [
        ("ATLANTE", "AMÉRICA"), ("XOLOS", "LEÓN"), ("CHIVAS", "JUÁREZ"),
        ("SANTOS", "ATLAS"), ("TOLUCA", "PUMAS"), ("PACHUCA", "TIGRES"),
        ("CRUZ AZUL", "MONTERREY"), ("PUEBLA", "SAN LUIS"), ("QUERÉTARO", "NECAXA")
    ],
    "J3": [
        ("JUÁREZ", "PUMAS"), ("QUERÉTARO", "TIGRES"), ("MONTERREY", "PUEBLA"),
        ("AMÉRICA", "PACHUCA"), ("ATLAS", "CRUZ AZUL"), ("LEÓN", "SANTOS"),
        ("SAN LUIS", "ATLANTE"), ("NECAXA", "CHIVAS"), ("TOLUCA", "XOLOS")
    ],
    "J4": [
        ("ATLANTE", "TOLUCA"), ("MONTERREY", "JUÁREZ"), ("ATLAS", "TIGRES"),
        ("PUMAS", "QUERÉTARO"), ("CRUZ AZUL", "LEÓN"), ("PUEBLA", "AMÉRICA"),
        ("CHIVAS", "SAN LUIS"), ("SANTOS", "NECAXA"), ("PACHUCA", "XOLOS")
    ],
    "J5": [
        ("JUÁREZ", "AMÉRICA"), ("QUERÉTARO", "TOLUCA"), ("CHIVAS", "XOLOS"),
        ("LEÓN", "MONTERREY"), ("TIGRES", "ATLAS"), ("PUMAS", "PUEBLA"),
        ("CRUZ AZUL", "PACHUCA"), ("ATLANTE", "SANTOS"), ("NECAXA", "SAN LUIS")
    ],
    "J6": [
        ("XOLOS", "PUMAS"), ("ATLAS", "QUERÉTARO"), ("PACHUCA", "CHIVAS"),
        ("AMÉRICA", "PUEBLA"), ("TOLUCA", "JUÁREZ"), ("MONTERREY", "ATLANTE"),
        ("SANTOS", "CRUZ AZUL"), ("TIGRES", "LEÓN"), ("SAN LUIS", "NECAXA")
    ],
    "J7": [
        ("PUEBLA", "TOLUCA"), ("JUÁREZ", "PACHUCA"), ("SAN LUIS", "CHIVAS"),
        ("QUERÉTARO", "MONTERREY"), ("AMÉRICA", "SANTOS"), ("CRUZ AZUL", "ATLANTE"),
        ("ATLAS", "PUMAS"), ("NECAXA", "LEÓN"), ("TIGRES", "XOLOS")
    ],
    "J8": [
        ("TOLUCA", "ATLAS"), ("CRUZ AZUL", "AMÉRICA"), ("SANTOS", "JUÁREZ"),
        ("CHIVAS", "PUMAS"), ("LEÓN", "QUERÉTARO"), ("MONTERREY", "TIGRES"),
        ("PUEBLA", "PACHUCA"), ("ATLANTE", "NECAXA"), ("XOLOS", "SAN LUIS")
    ],
    "J9": [
        ("PUEBLA", "ATLANTE"), ("JUÁREZ", "TIGRES"), ("ATLAS", "PUMAS"),
        ("SAN LUIS", "NECAXA"), ("AMÉRICA", "TOLUCA"), ("CRUZ AZUL", "CHIVAS"),
        ("PACHUCA", "LEÓN"), ("SANTOS", "MONTERREY"), ("QUERÉTARO", "XOLOS")
    ],
    "J10": [
        ("SANTOS", "PACHUCA"), ("TIGRES", "PUEBLA"), ("CRUZ AZUL", "TOLUCA"),
        ("PUMAS", "SAN LUIS"), ("AMÉRICA", "CHIVAS"), ("MONTERREY", "ATLAS"),
        ("LEÓN", "JUÁREZ"), ("ATLANTE", "QUERÉTARO"), ("XOLOS", "NECAXA")
    ],
    "J11": [
        ("QUERÉTARO", "ATLANTE"), ("PUEBLA", "LEÓN"), ("TIGRES", "TOLUCA"),
        ("JUÁREZ", "TIJUANA"), ("ATLAS", "CHIVAS"), ("AMÉRICA", "MONTERREY"),
        ("PACHUCA", "NECAXA"), ("SAN LUIS", "SANTOS"), ("PUMAS", "CRUZ AZUL")
    ],
    "J12": [
        ("NECAXA", "ATLAS"), ("ATLANTE", "PUMAS"), ("TIJUANA", "PUEBLA"),
        ("CHIVAS", "TIGRES"), ("SANTOS", "QUERÉTARO"), ("LEÓN", "AMÉRICA"),
        ("TOLUCA", "SAN LUIS"), ("CRUZ AZUL", "JUÁREZ"), ("MONTERREY", "PACHUCA")
    ],
    "J13": [
        ("SAN LUIS", "QUERÉTARO"), ("JUÁREZ", "ATLANTE"), ("TIGRES", "LEÓN"),
        ("CHIVAS", "NECAXA"), ("PUEBLA", "MONTERREY"), ("ATLAS", "AMÉRICA"),
        ("TOLUCA", "TIJUANA"), ("PACHUCA", "CRUZ AZUL"), ("SANTOS", "PUMAS")
    ],
    "J14": [
        ("NECAXA", "JUÁREZ"), ("ATLANTE", "SAN LUIS"), ("LEÓN", "TOLUCA"),
        ("MONTERREY", "CHIVAS"), ("PUMAS", "TIGRES"), ("ATLAS", "PUEBLA"),
        ("AMÉRICA", "PACHUCA"), ("QUERÉTARO", "CRUZ AZUL"), ("TIJUANA", "SANTOS")
    ],
    "J15": [
        ("SAN LUIS", "ATLAS"), ("JUÁREZ", "QUERÉTARO"), ("PUEBLA", "PUMAS"),
        ("PACHUCA", "TIGRES"), ("CHIVAS", "ATLANTE"), ("MONTERREY", "TIJUANA"),
        ("AMÉRICA", "TOLUCA"), ("SANTOS", "NECAXA"), ("CRUZ AZUL", "LEÓN")
    ],
    "J16": [
        ("SAN LUIS", "JUÁREZ"), ("NECAXA", "TIJUANA"), ("ATLANTE", "SANTOS"),
        ("ATLAS", "PACHUCA"), ("TIGRES", "CRUZ AZUL"), ("TOLUCA", "MONTERREY"),
        ("PUMAS", "AMÉRICA"), ("QUERÉTARO", "PUEBLA"), ("LEÓN", "CHIVAS")
    ],
    "J17": [
        ("PUEBLA", "SAN LUIS"), ("JUÁREZ", "ATLAS"), ("TIJUANA", "ATLANTE"),
        ("SANTOS", "LEÓN"), ("PACHUCA", "TOLUCA"), ("PUMAS", "MONTERREY"),
        ("TIGRES", "AMÉRICA"), ("CHIVAS", "CRUZ AZUL"), ("QUERÉTARO", "NECAXA")
    ]
}

LISTA_JORNADAS = [f"J{i}" for i in range(1, 18)]


def obtener_jornada_actual():
    hoy = date.today()
    for j, (f_inicio, f_fin) in CALENDARIO_JORNADAS.items():
        if f_inicio <= hoy <= f_fin:
            return j
    for j, (f_inicio, f_fin) in CALENDARIO_JORNADAS.items():
        if hoy < f_inicio:
            return j
    return "J17"


# --- BARRA LATERAL ---
st.sidebar.image("assets/logo_liga.png", width=380)
st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%); padding: 10px 15px; border-radius: 10px; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);">
        <span style="color: #ffffff; font-weight: 900; font-size: 1.1rem; letter-spacing: 1px;">⚡ PANEL ADMINISTRADOR</span>
    </div>
""", unsafe_allow_html=True)

jornada_automatica = obtener_jornada_actual()
st.sidebar.markdown(f"📅 **Fecha:** `{datetime.now().strftime('%d/%m/%Y')}`")
st.sidebar.markdown(f"⚽ **Jornada Sugerida:** `{jornada_automatica}`")
st.sidebar.markdown("---")

# =========================================================================
# PANEL DE CONTROL PRINCIPAL (ADMIN)
# =========================================================================
st.markdown("<h2 style='color: #a855f7; text-transform: uppercase;'>⚙ Panel de Control del Administrador</h2>",
            unsafe_allow_html=True)

default_index = LISTA_JORNADAS.index(jornada_automatica) if jornada_automatica in LISTA_JORNADAS else 0
jornada_sel = st.selectbox("Selecciona la jornada a gestionar:", LISTA_JORNADAS, index=default_index)
st.markdown(f"### Gestionando: <span style='color: #ec4899;'>{jornada_sel}</span>", unsafe_allow_html=True)
st.markdown("---")

# PESTAÑAS DE GESTIÓN
tab_tabla_sem, tab_premio, tab_participantes, tab_pronosticos, tab_resultados, tab_partidos = st.tabs([
    "🏆 Puntos de la Semana",
    "💰 Gestionar Premio",
    "👥 Participantes",
    "📝 Pronósticos",
    "⚽ Resultados",
    "🛠 Modificar Partidos"
])

# --- SECCIÓN: PUNTOS DE LA SEMANA ---
with tab_tabla_sem:
    st.markdown(f"#### Clasificación Semanal - {jornada_sel}")
    rows_j = obtener_datos_jornada_cache(jornada_sel.upper())

    if rows_j and len(rows_j) >= 4:
        bolsa_texto = "PREMIO $0"
        for val_c in rows_j[1]:
            if val_c and str(val_c).strip() != "":
                bolsa_texto = str(val_c).strip()
                break

        monto_bolsa = 0
        match_bolsa = re.search(r'\d+', bolsa_texto.replace(',', ''))
        if match_bolsa:
            monto_bolsa = int(match_bolsa.group())

        tabla_semanal_data = []
        for r in rows_j:
            if not r: continue
            if len(r) > 1 and str(r[1]).strip() != "" and str(r[1]).strip().upper() != "NOMBRE":
                nombre_p = str(r[1]).strip()
                pts_p = int(float(str(r[21]).strip())) if len(r) > 21 and str(r[21]).strip().replace('.', '',
                                                                                                     1).isdigit() else 0
                tabla_semanal_data.append({"Participante": nombre_p, "Puntos": pts_p})
            if len(r) > 23 and str(r[23]).strip() != "" and str(r[23]).strip().upper() != "NOMBRE":
                nombre_p = str(r[23]).strip()
                pts_p = int(float(str(r[43]).strip())) if len(r) > 43 and str(r[43]).strip().replace('.', '',
                                                                                                     1).isdigit() else 0
                tabla_semanal_data.append({"Participante": nombre_p, "Puntos": pts_p})

        if tabla_semanal_data:
            df_sem = pd.DataFrame(tabla_semanal_data)
            df_sem = df_sem.sort_values(by="Puntos", ascending=False).reset_index(drop=True)

            max_pts = df_sem["Puntos"].max() if not df_sem.empty else 0
            ganadores_count = len(df_sem[df_sem["Puntos"] == max_pts]) if max_pts > 0 else 1
            premio_por_ganador = int(monto_bolsa / max(ganadores_count, 1))

            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #312e81 0%, #4338ca 100%); border: 2px solid #a855f7; border-radius: 12px; padding: 14px 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);">
                    <div>
                        <span style="color: #c084fc; font-size: 0.8rem; font-weight: bold; text-transform: uppercase;">💰 Bolsa Total ({jornada_sel})</span>
                        <div style="font-size: 1.3rem; font-weight: 900; color: #ffffff;">{bolsa_texto}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: #34d399; font-size: 0.8rem; font-weight: bold; text-transform: uppercase;">🏆 Premio x Ganador (Empates)</span>
                        <div style="font-size: 1.3rem; font-weight: 900; color: #34d399;">${premio_por_ganador:,}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            leaderboard_html = """
            <style>
                .lb-admin-container { display: flex; flex-direction: column; gap: 10px; max-height: 650px; overflow-y: auto; padding: 5px; }
                .lb-admin-row { display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 12px; padding: 14px 20px; }
                .lb-admin-gold { background: linear-gradient(135deg, #713f12 0%, #312e81 100%) !important; border: 2px solid #fbbf24 !important; box-shadow: 0 0 15px rgba(251, 191, 36, 0.3); }
                .lb-admin-left { display: flex; align-items: center; gap: 15px; }
                .lb-admin-rank { font-size: 1.2rem; font-weight: 900; color: #c084fc; width: 60px; text-align: center; }
                .lb-admin-name { font-size: 1.15rem; font-weight: bold; color: #ffffff; }
                .lb-admin-points { font-size: 1.4rem; font-weight: 900; color: #34d399; }
            </style>
            <div class="lb-admin-container">
            """

            for idx, row in df_sem.iterrows():
                is_first = (idx == 0 or row["Puntos"] == max_pts) and max_pts > 0
                row_cls = "lb-admin-row lb-admin-gold" if is_first else "lb-admin-row"

                if idx == 0:
                    rank_str = "🥇 #1"
                elif idx == 1:
                    rank_str = "🥈 #2"
                elif idx == 2:
                    rank_str = "🥉 #3"
                else:
                    rank_str = f"#{idx + 1}"

                leaderboard_html += f"""
                    <div class="{row_cls}">
                        <div class="lb-admin-left">
                            <div class="lb-admin-rank">{rank_str}</div>
                            <div class="lb-admin-name">{row["Participante"]}</div>
                        </div>
                        <div class="lb-admin-points">{row["Puntos"]} PTS</div>
                    </div>
                """
            leaderboard_html += "</div>"
            components.html(leaderboard_html, height=670, scrolling=True)

with tab_premio:
    st.markdown(f"#### Actualizar Premio para {jornada_sel}")
    rows_j = obtener_datos_jornada_cache(jornada_sel.upper())
    premio_actual = ""
    if len(rows_j) >= 2:
        for val_c in rows_j[1]:
            if val_c and str(val_c).strip() != "":
                premio_actual = str(val_c).strip()
                break
    input_premio = st.text_input("Monto o descripción del premio:", value=premio_actual)
    if st.button("Guardar Premio en Google Sheets", type="primary"):
        spreadsheet = conectar_google_sheets()
        if spreadsheet:
            try:
                limpio = input_premio.strip().replace("$", "").replace(",", "")
                nuevo_premio = f"PREMIO ${int(limpio):,}" if limpio.isdigit() else input_premio.strip().upper()
                sheet_j = spreadsheet.worksheet(jornada_sel.upper())
                sheet_j.update_acell('B2', nuevo_premio)
                sheet_j.update('A2', [[nuevo_premio]])
                sheet_j.update_acell('B165', nuevo_premio)
                sheet_j.update('A165', [[nuevo_premio]])
                st.cache_data.clear()
                st.success("¡Premio actualizado exitosamente en ambos bloques!")
            except Exception as e:
                st.error(f"Error: {e}")

# --- SECCIÓN: AGREGAR / ELIMINAR PARTICIPANTES ---
with tab_participantes:
    st.markdown(f"#### Gestión de Participantes - {jornada_sel}")
    st.info(f"Agrega nuevos participantes o elimina participantes existentes de la {jornada_sel}.")

    rows_j = obtener_datos_jornada_cache(jornada_sel.upper())
    participantes_activos = []

    if rows_j:
        for r_idx, r in enumerate(rows_j):
            if not r: continue
            if len(r) > 1 and str(r[1]).strip() != "" and str(r[1]).strip().upper() not in ["NOMBRE", "PARTICIPANTE",
                                                                                            "TOTAL", "PUNTOS"]:
                participantes_activos.append({"nombre": str(r[1]).strip(), "fila": r_idx + 1, "col_nombre": 2})
            if len(r) > 23 and str(r[23]).strip() != "" and str(r[23]).strip().upper() not in ["NOMBRE", "PARTICIPANTE",
                                                                                               "TOTAL", "PUNTOS"]:
                participantes_activos.append({"nombre": str(r[23]).strip(), "fila": r_idx + 1, "col_nombre": 24})

    col_add, col_del = st.columns(2, gap="large")

    with col_add:
        st.markdown("##### ➕ Agregar Nuevo Participante")
        nuevo_p_input = st.text_input("Nombre del nuevo participante:",
                                      key=f"input_nuevo_participante_{jornada_sel}").strip().upper()
        if st.button("Registrar Nuevo Participante", type="primary", key=f"btn_add_{jornada_sel}"):
            if nuevo_p_input:
                spreadsheet = conectar_google_sheets()
                if spreadsheet:
                    try:
                        sheet_j = spreadsheet.worksheet(jornada_sel.upper())
                        current_rows = sheet_j.get_all_values()
                        row_to_use = -1

                        for r_idx in range(136, 166):
                            val_x = ""
                            if r_idx < len(current_rows) and len(current_rows[r_idx]) > 23:
                                val_x = str(current_rows[r_idx][23]).strip()
                            if not val_x:
                                row_to_use = r_idx + 1
                                break

                        if row_to_use != -1:
                            fila_modelo = row_to_use - 1
                            numero_anterior = 0
                            if fila_modelo - 1 < len(current_rows) and len(current_rows[fila_modelo - 1]) > 22:
                                val_prev = str(current_rows[fila_modelo - 1][22]).strip()
                                if val_prev.isdigit():
                                    numero_anterior = int(val_prev)

                            siguiente_numero = numero_anterior + 1 if numero_anterior > 0 else 1

                            rango_modelo = sheet_j.range(f"W{fila_modelo}:ZZ{fila_modelo}")
                            rango_destino = sheet_j.range(f"W{row_to_use}:ZZ{row_to_use}")
                            for cell_src, cell_dst in zip(rango_modelo, rango_destino):
                                cell_dst.value = cell_src.value
                            sheet_j.update_cells(rango_destino)

                            sheet_j.format(f"X{row_to_use}", {
                                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                                "textFormat": {"fontFamily": "Calibri", "fontSize": 18, "bold": True},
                                "horizontalAlignment": "LEFT"
                            })
                            sheet_j.format(f"Y{row_to_use}:ZZ{row_to_use}", {
                                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                                "textFormat": {"fontFamily": "Calibri", "fontSize": 18, "bold": False},
                                "horizontalAlignment": "CENTER"
                            })

                            sheet_j.update_acell(f'W{row_to_use}', siguiente_numero)
                            sheet_j.update_acell(f'X{row_to_use}', nuevo_p_input)

                            formula_ar = f"=SUMA(AA{row_to_use},AC{row_to_use},AE{row_to_use},AG{row_to_use},AI{row_to_use},AK{row_to_use},AM{row_to_use},AO{row_to_use},AQ{row_to_use})"
                            sheet_j.update_acell(f'AR{row_to_use}', formula_ar)

                            st.cache_data.clear()
                            st.success(
                                f"✅ ¡Se agregó a '{nuevo_p_input}' con ID {siguiente_numero} en la fila {row_to_use} y su fórmula aplicada!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("⚠️ No hay espacio disponible en el rango de celdas X137:X166 de esta jornada.")
                    except Exception as e:
                        st.error(f"Error al agregar participante: {e}")
            else:
                st.error("Ingresa un nombre válido.")

    with col_del:
        st.markdown("##### ➖ Eliminar Participante")
        if participantes_activos:
            nombres_activos_list = [p["nombre"] for p in participantes_activos]
            p_a_eliminar = st.selectbox("Selecciona al participante a eliminar:", nombres_activos_list,
                                        key=f"select_eliminar_participante_{jornada_sel}")

            if st.button("Eliminar Participante Seleccionado", type="secondary", key=f"btn_del_{jornada_sel}"):
                spreadsheet = conectar_google_sheets()
                if spreadsheet:
                    try:
                        sheet_j = spreadsheet.worksheet(jornada_sel.upper())
                        p_info = next((p for p in participantes_activos if p["nombre"] == p_a_eliminar), None)
                        if p_info:
                            fila_del = p_info["fila"]
                            col_del_idx = p_info["col_nombre"]

                            indices_a_limpiar = range(col_del_idx - 1, col_del_idx + 21)
                            for c_idx in indices_a_limpiar:
                                col_letra_limpiar = gspread.utils.rowcol_to_a1(1, c_idx + 1).replace('1', '')
                                sheet_j.update_acell(f"{col_letra_limpiar}{fila_del}", "")

                            st.cache_data.clear()
                            st.success(f"✅ ¡Se eliminó con éxito al participante '{p_a_eliminar}'!")
                            st.rerun()
                        else:
                            st.error("No se encontró el participante seleccionado.")
                    except Exception as e:
                        st.error(f"Error al eliminar participante: {e}")
        else:
            st.info("No hay participantes registrados actualmente en esta jornada.")

# --- SECCIÓN: PRONÓSTICOS PARTICIPANTES ---
with tab_pronosticos:
    st.markdown(f"#### Captura o Edición de Pronósticos - {jornada_sel}")
    rows_j = obtener_datos_jornada_cache(jornada_sel.upper())

    if rows_j and len(rows_j) >= 4:
        participantes_map = {}
        for r_idx, r in enumerate(rows_j):
            if not r: continue
            if len(r) > 1 and str(r[1]).strip() != "" and str(r[1]).strip().upper() not in ["NOMBRE", "PARTICIPANTE",
                                                                                            "TOTAL", "PUNTOS"]:
                nom_izq = str(r[1]).strip()
                participantes_map[nom_izq.upper()] = {"nombre": nom_izq, "fila": r_idx + 1, "col_nombre": 2,
                                                      "bloque": "izq"}
            if len(r) > 23 and str(r[23]).strip() != "" and str(r[23]).strip().upper() not in ["NOMBRE", "PARTICIPANTE",
                                                                                               "TOTAL", "PUNTOS"]:
                nom_der = str(r[23]).strip()
                participantes_map[nom_der.upper()] = {"nombre": nom_der, "fila": r_idx + 1, "col_nombre": 24,
                                                      "bloque": "der"}

        nombres_ordenados = sorted(list(participantes_map.keys()))

        busqueda_input = st.text_input("🔍 Escribe el nombre del participante a buscar:",
                                       key=f"busqueda_pron_{jornada_sel}").strip().upper()
        coincidencias = [n for n in nombres_ordenados if busqueda_input in n] if busqueda_input else nombres_ordenados

        if len(coincidencias) > 0:
            participante_seleccionado = st.selectbox("Selecciona de la lista de coincidencias:", coincidencias,
                                                     key=f"sel_pron_{jornada_sel}")
        else:
            participante_seleccionado = "NUEVO"

        exactamente_existe = (busqueda_input in nombres_ordenados) or (
                    participante_seleccionado in nombres_ordenados and busqueda_input == participante_seleccionado)

        if busqueda_input and not exactamente_existe:
            st.warning(f"⚠️ El participante **'{busqueda_input}'** no está registrado en esta jornada.")
            if st.button(f"➕ Agregar a '{busqueda_input}' a la {jornada_sel}", type="primary",
                         key=f"btn_add_pron_{jornada_sel}"):
                spreadsheet = conectar_google_sheets()
                if spreadsheet:
                    try:
                        sheet_j = spreadsheet.worksheet(jornada_sel.upper())
                        current_rows = sheet_j.get_all_values()
                        row_to_use = -1
                        for r_idx in range(136, 166):
                            val_x = ""
                            if r_idx < len(current_rows) and len(current_rows[r_idx]) > 23:
                                val_x = str(current_rows[r_idx][23]).strip()
                            if not val_x:
                                row_to_use = r_idx + 1
                                break

                        if row_to_use != -1:
                            fila_modelo = row_to_use - 1
                            numero_anterior = 0
                            if fila_modelo - 1 < len(current_rows) and len(current_rows[fila_modelo - 1]) > 22:
                                val_prev = str(current_rows[fila_modelo - 1][22]).strip()
                                if val_prev.isdigit():
                                    numero_anterior = int(val_prev)

                            siguiente_numero = numero_anterior + 1 if numero_anterior > 0 else 1

                            rango_modelo = sheet_j.range(f"W{fila_modelo}:ZZ{fila_modelo}")
                            rango_destino = sheet_j.range(f"W{row_to_use}:ZZ{row_to_use}")
                            for cell_src, cell_dst in zip(rango_modelo, rango_destino):
                                cell_dst.value = cell_src.value
                            sheet_j.update_cells(rango_destino)

                            sheet_j.format(f"X{row_to_use}", {
                                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                                "textFormat": {"fontFamily": "Calibri", "fontSize": 18, "bold": True},
                                "horizontalAlignment": "LEFT"
                            })
                            sheet_j.format(f"Y{row_to_use}:ZZ{row_to_use}", {
                                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                                "textFormat": {"fontFamily": "Calibri", "fontSize": 18, "bold": False},
                                "horizontalAlignment": "CENTER"
                            })

                            sheet_j.update_acell(f'W{row_to_use}', siguiente_numero)
                            sheet_j.update_acell(f'X{row_to_use}', busqueda_input)

                            formula_ar = f"=SUMA(AA{row_to_use},AC{row_to_use},AE{row_to_use},AG{row_to_use},AI{row_to_use},AK{row_to_use},AM{row_to_use},AO{row_to_use},AQ{row_to_use})"
                            sheet_j.update_acell(f'AR{row_to_use}', formula_ar)

                            st.cache_data.clear()
                            st.success(f"✅ ¡Se agregó con éxito al participante '{busqueda_input}' con su fórmula!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("No hay espacio disponible en el bloque derecho (X137:X166).")
                    except Exception as e:
                        st.error(f"Error al agregar participante: {e}")

        if participante_seleccionado and participante_seleccionado != "NUEVO" and participante_seleccionado in participantes_map:
            info_p = participantes_map[participante_seleccionado]
            fila_idx = info_p["fila"] - 1
            es_izq = (info_p["bloque"] == "izq")
            indices_pronosticos = [3, 5, 7, 9, 11, 13, 15, 17, 19] if es_izq else [25, 27, 29, 31, 33, 35, 37, 39, 41]

            st.markdown(
                f"Editando pronósticos de: **{info_p['nombre']}** (Bloque {'Izquierdo' if es_izq else 'Derecho'})")

            enfrentamientos = [f"Partido {i + 1}" for i in range(9)]
            try:
                for i in range(9):
                    fila_local = 4 + (i * 4)
                    idx_l = fila_local - 1
                    loc_t = str(rows_j[idx_l][44]).strip() if idx_l < len(rows_j) and len(rows_j[idx_l]) > 44 else ""
                    idx_v = (4 + (i * 4)) + 1 - 1
                    vis_t = str(rows_j[idx_v][44]).strip() if idx_v < len(rows_j) and len(rows_j[idx_v]) > 44 else ""
                    if loc_t and vis_t:
                        enfrentamientos[i] = f"{loc_t} vs {vis_t}"
            except Exception:
                pass

            row_data = rows_j[fila_idx] if fila_idx < len(rows_j) else []
            pronosticos_actuales = []
            for c_idx in indices_pronosticos:
                val_p = str(row_data[c_idx]).strip().upper() if c_idx < len(row_data) else ""
                if val_p not in ["L", "E", "V"]: val_p = "L"
                pronosticos_actuales.append(val_p)

            with st.form(key=f"form_pronosticos_{info_p['nombre']}_{jornada_sel}"):
                nuevos_pronosticos = []
                cols_form = st.columns(3)

                opciones_validas = ["L", "E", "V"]
                for i in range(9):
                    idx_default = opciones_validas.index(pronosticos_actuales[i]) if pronosticos_actuales[
                                                                                         i] in opciones_validas else 0
                    with cols_form[i % 3]:
                        val_sel = st.selectbox(f"Juego {i + 1}: {enfrentamientos[i]}", opciones_validas,
                                               index=idx_default, key=f"p_{i}_{info_p['nombre']}_{jornada_sel}")
                        nuevos_pronosticos.append(val_sel)

                submit_btn = st.form_submit_button("💾 Guardar Pronósticos en Google Sheets", type="primary")
                if submit_btn:
                    spreadsheet = conectar_google_sheets()
                    if spreadsheet:
                        try:
                            sheet_j = spreadsheet.worksheet(jornada_sel.upper())
                            for i, c_idx in enumerate(indices_pronosticos):
                                col_letra = gspread.utils.rowcol_to_a1(info_p["fila"], c_idx + 1)
                                letra_columna = ''.join([c for c in col_letra if c.isalpha()])
                                celda_exacta = f"{letra_columna}{info_p['fila']}"
                                sheet_j.update_acell(celda_exacta, nuevos_pronosticos[i])

                            st.cache_data.clear()
                            st.success(
                                f"✅ ¡Pronósticos de {info_p['nombre']} actualizados correctamente en Google Sheets!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar pronósticos: {e}")

# --- SECCIÓN: RESULTADOS DE PARTIDOS ---
with tab_resultados:
    st.markdown(f"#### Captura de Resultados Oficiales - {jornada_sel}")
    st.info(
        "Selecciona el resultado oficial (L = Local, E = Empate, V = Visitante) para cada partido de la jornada. Esto actualizará el puntaje de todos los participantes automáticamente.")

    rows_j = obtener_datos_jornada_cache(jornada_sel.upper())

    if rows_j and len(rows_j) >= 4:
        enfrentamientos = [f"Partido {i + 1}" for i in range(9)]
        celdas_resultados = []
        resultados_actuales = []

        try:
            for i in range(9):
                fila_res = 6 + (i * 4)
                celda_exacta = f"AV{fila_res}"
                celdas_resultados.append(celda_exacta)

                fila_local = 4 + (i * 4)
                fila_visitante = 5 + (i * 4)

                loc_t = str(rows_j[fila_local - 1][44]).strip() if (fila_local - 1) < len(rows_j) and len(
                    rows_j[fila_local - 1]) > 44 else ""
                vis_t = str(rows_j[fila_visitante - 1][44]).strip() if (fila_visitante - 1) < len(rows_j) and len(
                    rows_j[fila_visitante - 1]) > 44 else ""

                if loc_t and vis_t:
                    enfrentamientos[i] = f"{loc_t} vs {vis_t}"

                res_val = ""
                idx_res_0 = fila_res - 1
                if idx_res_0 < len(rows_j) and len(rows_j[idx_res_0]) > 47:
                    res_val = str(rows_j[idx_res_0][47]).strip().upper()

                if res_val not in ["L", "E", "V"]:
                    res_val = "L"
                resultados_actuales.append(res_val)

        except Exception as e:
            st.error(f"Error al analizar los partidos: {e}")

        with st.form(key=f"form_resultados_{jornada_sel}"):
            nuevos_resultados = []
            cols_res = st.columns(3)
            opciones_res = ["L", "E", "V"]

            for i in range(9):
                idx_def = opciones_res.index(resultados_actuales[i]) if resultados_actuales[i] in opciones_res else 0
                with cols_res[i % 3]:
                    res_sel = st.selectbox(f"Partido {i + 1}: {enfrentamientos[i]}", opciones_res, index=idx_def,
                                           key=f"res_oficial_{i}_{jornada_sel}")
                    nuevos_resultados.append(res_sel)

            submit_res_btn = st.form_submit_button("💾 Guardar Resultados Oficiales en Google Sheets", type="primary")
            if submit_res_btn:
                spreadsheet = conectar_google_sheets()
                if spreadsheet:
                    try:
                        sheet_j = spreadsheet.worksheet(jornada_sel.upper())
                        for i, celda_dest in enumerate(celdas_resultados):
                            sheet_j.update_acell(celda_dest, nuevos_resultados[i])

                        st.cache_data.clear()
                        st.success("✅ ¡Resultados oficiales guardados y actualizados exitosamente en Google Sheets!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar resultados oficiales: {e}")
    else:
        st.warning("No se pudo cargar la información de los partidos para esta jornada.")

# --- SECCIÓN: MODIFICAR PARTIDOS ---
with tab_partidos:
    st.markdown(f"#### 🛠 Modificar Enfrentamientos / Equipos - {jornada_sel}")
    st.info(
        "Actualiza los nombres de los equipos Local y Visitante para cada uno de los 9 partidos de la jornada o cárgalos automáticamente con el calendario oficial.")

    st.markdown("""
        <style>
        div.stButton > button[kind="secondary"] {
            background: linear-gradient(135deg, #3b82f6 100%, #1d4ed8 0%);
            color: white;
            font-size: 1.15rem !important;
            font-weight: 800 !important;
            padding: 0.8rem 2rem !important;
            border-radius: 12px;
            border: 2px solid #60a5fa;
            width: 100%;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        }
        div.stButton > button[kind="secondary"]:hover {
            background: linear-gradient(135deg, #2563eb 100%, #1e40af 0%);
            border-color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button(f"📥 CARGAR PARTIDOS OFICIALES DE {jornada_sel.upper()}", type="secondary",
                 key=f"btn_autocargar_{jornada_sel}"):
        if jornada_sel in PARTIDOS_OFICIALES_APERTURA_2026:
            spreadsheet = conectar_google_sheets()
            if spreadsheet:
                try:
                    sheet_j = spreadsheet.worksheet(jornada_sel.upper())
                    partidos_oficiales = PARTIDOS_OFICIALES_APERTURA_2026[jornada_sel]

                    for i, (loc, vis) in enumerate(partidos_oficiales):
                        fila_local = 4 + (i * 4)
                        fila_visitante = 5 + (i * 4)

                        sheet_j.update_acell(f"AS{fila_local}", loc)
                        sheet_j.update_acell(f"AS{fila_visitante}", vis)

                    st.cache_data.clear()
                    st.success(
                        f"✅ ¡Partidos oficiales de la {jornada_sel} cargados correctamente en Google Sheets (Columna AS)!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al autocargar partidos: {e}")
        else:
            st.warning("No hay partidos oficiales registrados para esta jornada.")

    st.markdown("---")

    rows_j = obtener_datos_jornada_cache(jornada_sel.upper())

    if rows_j and len(rows_j) >= 4:
        partidos_guardados = []
        try:
            for i in range(9):
                fila_local = 4 + (i * 4)
                fila_visitante = 5 + (i * 4)

                local_actual = ""
                visitante_actual = ""

                if (fila_local - 1) < len(rows_j) and len(rows_j[fila_local - 1]) > 44:
                    local_actual = str(rows_j[fila_local - 1][44]).strip()

                if (fila_visitante - 1) < len(rows_j) and len(rows_j[fila_visitante - 1]) > 44:
                    visitante_actual = str(rows_j[fila_visitante - 1][44]).strip()

                if not local_actual: local_actual = "Local por definir"
                if not visitante_actual: visitante_actual = "Visitante por definir"

                partidos_guardados.append({
                    "n_partido": i + 1,
                    "local": local_actual,
                    "fila_local": fila_local,
                    "visitante": visitante_actual,
                    "fila_visitante": fila_visitante
                })
        except Exception as e:
            st.error(f"Error al extraer los partidos: {e}")
            partidos_guardados = []

        if partidos_guardados:
            st.markdown("### 🏟️ Vista Previa de Enfrentamientos Actuales", unsafe_allow_html=True)
            cols_cards = st.columns(3)
            for i, p in enumerate(partidos_guardados):
                with cols_cards[i % 3]:
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); border: 1px solid rgba(168, 85, 247, 0.4); border-radius: 12px; padding: 18px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.4); text-align: center;">
                            <div style="font-size: 0.8rem; font-weight: bold; color: #c084fc; text-transform: uppercase; margin-bottom: 10px;">Partido {p['n_partido']}</div>
                            <div style="font-size: 1.2rem; font-weight: 900; color: #ffffff; margin-bottom: 6px;">🏠 {p['local']}</div>
                            <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 6px; font-weight: bold;">VS</div>
                            <div style="font-size: 1.2rem; font-weight: 900; color: #ffffff;">✈️ {p['visitante']}</div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### ✏️ Edición Manual de Enfrentamientos", unsafe_allow_html=True)

            with st.form(key=f"form_modificar_partidos_{jornada_sel}"):
                nuevos_equipos = []
                for p in partidos_guardados:
                    st.markdown(f"##### ⚽ Partido {p['n_partido']}")
                    col_loc, col_vis = st.columns(2)
                    with col_loc:
                        l_val = "" if p['local'] == "Local por definir" else p['local']
                        nuevo_local = st.text_input(f"Local - Juego {p['n_partido']}", value=l_val,
                                                    key=f"loc_{p['n_partido']}_{jornada_sel}")
                    with col_vis:
                        v_val = "" if p['visitante'] == "Visitante por definir" else p['visitante']
                        nuevo_visitante = st.text_input(f"Visitante - Juego {p['n_partido']}", value=v_val,
                                                        key=f"vis_{p['n_partido']}_{jornada_sel}")

                    nuevos_equipos.append({
                        "fila_local": p['fila_local'],
                        "local": nuevo_local.strip().upper(),
                        "fila_visitante": p['fila_visitante'],
                        "visitante": nuevo_visitante.strip().upper()
                    })
                    st.markdown("---")

                submit_partidos_btn = st.form_submit_button("💾 Guardar Cambios de Partidos en Google Sheets",
                                                            type="primary")
                if submit_partidos_btn:
                    spreadsheet = conectar_google_sheets()
                    if spreadsheet:
                        try:
                            sheet_j = spreadsheet.worksheet(jornada_sel.upper())
                            for item in nuevos_equipos:
                                sheet_j.update_acell(f"AS{item['fila_local']}", item['local'])
                                sheet_j.update_acell(f"AS{item['fila_visitante']}", item['visitante'])

                            st.cache_data.clear()
                            st.success(
                                "✅ ¡Los enfrentamientos y nombres de equipos se actualizaron correctamente en la columna AS de Google Sheets!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al actualizar los partidos en Google Sheets: {e}")
    else:
        st.warning("No se pudieron cargar los datos de los partidos para esta jornada.")