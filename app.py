import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time, date
import re
from fpdf import FPDF
import json
import os
import pdfplumber
import folium
from streamlit.components.v1 import html as st_html

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Horários MUV Viseu - Linhas C1 e C2",
    page_icon="🚌",
    layout="wide"
)

# --- CACHE / PERSISTENCE FILE ---
CACHE_FILE = "custom_schedules.json"

# --- DEFAULT DATA (OFFICIAL LATEST: 1 DE MARÇO DE 2026) ---
DEFAULT_VERSION_DATE = "2026-03-01"
DEFAULT_VERSION_LABEL = "1 de Março de 2026"

DEFAULT_DEPARTURES_DIAS_UTEIS = [
    "06:30", "06:50", "07:10", "07:30", "07:50", "08:10", "08:30", "08:50",
    "09:10", "09:30", "09:50", "10:10", "10:30", "10:50", "11:10", "11:30",
    "11:50", "12:10", "12:30", "12:50", "13:10", "13:30", "13:50", "14:10",
    "14:30", "14:50", "15:10", "15:30", "15:50", "16:10", "16:30", "16:50",
    "17:10", "17:30", "17:50", "18:10", "18:30", "18:50", "19:50"
]

DEFAULT_DEPARTURES_SABADOS = [
    "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"
]

DEFAULT_DEPARTURES_DOMINGOS = [
    "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00"
]

DEFAULT_STOPS_C1 = [
    ('Interface Hospital', 0, 40.6582, -7.9065),
    ('Rei D Duarte-Hospital 1', 1, 40.6575, -7.908),
    ('Quinta D´el Rei', 2, 40.656, -7.909),
    ('Dr A Alves-C Comercial 1', 3, 40.6545, -7.9105),
    ('Quinta do Galo 2', 4, 40.6536, -7.9114),
    ('Quinta de Jugueiros', 5, 40.6515, -7.9135),
    ('Residências IPV', 6, 40.6495, -7.915),
    ('Rua Nova', 7, 40.648, -7.916),
    ('Cidade Politécnica-IPV', 8, 40.6465, -7.917),
    ('Reg Infantaria-IPV 1', 9, 40.6485, -7.918),
    ('Reg Infantaria-IPV 2', 10, 40.6506, -7.9179),
    ('Paulo VI-25 Abril', 11, 40.652, -7.915),
    ('25 Abril-Liceu 2', 12, 40.6546, -7.9124),
    ('Rossio 2', 13, 40.6574, -7.9122),
    ('Alberto Sampaio 1', 14, 40.658, -7.911),
    ('Alberto Sampaio 2', 15, 40.6596, -7.9089),
    ('N. S. Fátima-Igreja', 16, 40.6605, -7.908),
    ('J Maria Escrivá-Hotel 2', 17, 40.6626, -7.9064),
    ('José Maria Escrivá 2', 18, 40.6641, -7.9054),
    ('Monte Belo-J Infância 1', 19, 40.665, -7.905),
    ('Monte Belo-Estádio 1', 20, 40.6665, -7.904),
    ('Campo dos Trambelos', 21, 40.668, -7.903),
    ('Balsa 1', 22, 40.669, -7.902),
    ('César Anjo 1', 23, 40.67, -7.901),
    ('Bombeiros Voluntários', 24, 40.6685, -7.908),
    ('COMV 1', 25, 40.667, -7.912),
    ('Fonte Cibernética 2', 26, 40.6666, -7.9144),
    ('Av Europa-Tribunal 2', 27, 40.6656, -7.9174),
    ('M Ferreira Figueiredo 1', 30, 40.668, -7.922),
    ('Pedro Henriques 1', 31, 40.67, -7.924),
    ('Escola Viriato 2', 33, 40.6726, -7.9254),
    ('Estrada Velha Abraveses', 35, 40.674, -7.928),
    ('Cava de Viriato 2', 37, 40.6656, -7.9124),
    ('Feira de S. Mateus 2', 38, 40.6626, -7.9129),
    ('Porta dos Cavaleiros 1', 39, 40.6595, -7.9125),
    ('Mouzinho de Albuquerque', 40, 40.658, -7.914),
    ('Capitão Silva Pereira', 41, 40.657, -7.9155),
    ('Cap S Pereira-S Cristina', 42, 40.656, -7.9165),
    ('5 de Outubro 1', 43, 40.655, -7.915),
    ('Rua Seminário', 44, 40.654, -7.9135),
    ('Dr Azeredo Perdigão 1', 45, 40.655, -7.912),
    ('General Humberto Delgado', 46, 40.656, -7.9125),
    ('Rossio 1', 48, 40.657, -7.9126),
    ('25 Abril-Liceu 1', 50, 40.6542, -7.9128),
    ('Nuno Alvares Pereira', 51, 40.6525, -7.914),
    ('Escola João de Barros 1', 52, 40.651, -7.913),
    ('Manuel Silva Almeida 1', 53, 40.65, -7.912),
    ('Paulo VI-25 Abril (Regresso)', 54, 40.6528, -7.9142),
    ('Escola Grão Vasco', 55, 40.6535, -7.911),
    ('Alexandre Lucena e Vale', 56, 40.655, -7.909),
    ('10 de Junho-Cemitério 1', 57, 40.6565, -7.9075),
    ('Rei D Duarte-Mesuras', 58, 40.6575, -7.907),
    ('Hospital S Teotónio', 58, 40.658, -7.9068),
    ('Interface Hospital (Chegada)', 60, 40.659, -7.9057)
]

DEFAULT_STOPS_C2 = [
    ('Interface Hospital', 0, 40.6582, -7.9065),
    ('Biblioteca-Loja Cidadão', 1, 40.657, -7.908),
    ('10 de Junho-Cemitério 2', 2, 40.6571, -7.9069),
    ('Rua Mendonça', 3, 40.655, -7.909),
    ('Escola Grão Vasco', 3, 40.6535, -7.911),
    ('Praça de Goa', 4, 40.652, -7.912),
    ('Estevão Lopes Morago 1', 5, 40.651, -7.9125),
    ('Manuel Silva Almeida 2', 6, 40.6506, -7.9114),
    ('Escola João de Barros 2', 7, 40.6516, -7.9124),
    ('António Esteves Correia', 8, 40.6525, -7.9135),
    ('25 Abril-Liceu 2', 9, 40.6546, -7.9124),
    ('Rossio 2', 10, 40.6574, -7.9122),
    ('Alves Martins', 11, 40.6575, -7.9135),
    ('Dr Azeredo Perdigão 2', 12, 40.6556, -7.9114),
    ('Monsenhor Celso T Silva', 13, 40.6545, -7.914),
    ('Universidade Católica', 14, 40.6535, -7.916),
    ('5 de Outubro 2', 15, 40.6556, -7.9144),
    ('S Cristina-Cap S Pereira', 16, 40.656, -7.9165),
    ('Cap S Pereira-Fontelo', 17, 40.6575, -7.915),
    ('Largo Santo António', 18, 40.6585, -7.9135),
    ('Porta dos Cavaleiros 2', 19, 40.6601, -7.9119),
    ('Feira de S Mateus 1', 20, 40.662, -7.9135),
    ('Cava de Viriato 1', 21, 40.665, -7.913),
    ('Av Bélgica-Alf Miguel 1', 22, 40.667, -7.918),
    ('Avenida Bélgica 2', 23, 40.6691, -7.9194),
    ('Pedro Henriques 1', 24, 40.67, -7.924),
    ('Pedro Henriques 2', 25, 40.6716, -7.9244),
    ('M Ferreira Figueiredo 2', 27, 40.6686, -7.9214),
    ('Avenida Europa', 29, 40.666, -7.92),
    ('Av Europa-Tribunal 1', 31, 40.665, -7.918),
    ('Fonte Cibernética 1', 32, 40.666, -7.915),
    ('COMV 2', 33, 40.6676, -7.9114),
    ('César Anjo 2', 34, 40.6706, -7.9004),
    ('Balsa 2', 35, 40.6696, -7.9014),
    ('Cidade Aveiro', 36, 40.6675, -7.903),
    ('Monte Belo-Estádio 2', 37, 40.6671, -7.9034),
    ('Monte Belo-J Infância 2', 38, 40.6656, -7.9044),
    ('José Maria Escrivá 1', 39, 40.6635, -7.906),
    ('J Maria Escrivá-Hotel 1', 40, 40.662, -7.907),
    ('Engrácia Carrilho-Igreja', 41, 40.66, -7.9085),
    ('Colégio Imac Conceição', 42, 40.659, -7.91),
    ('Alberto Sampaio 3', 43, 40.658, -7.911),
    ('Rossio 1', 44, 40.657, -7.9126),
    ('25 Abril-Liceu 1', 45, 40.6542, -7.9128),
    ('25 Abril-Paulo VI', 45, 40.652, -7.915),
    ('Reg Infantaria', 46, 40.65, -7.9185),
    ('Reg Infantaria-IPV 3', 47, 40.6485, -7.918),
    ('C Politécnica-Escola', 48, 40.6465, -7.917),
    ('Madre Rita de Jesus 1', 49, 40.648, -7.9155),
    ('M Rita Jesus-Escola 1', 50, 40.6495, -7.914),
    ('M Rita Jesus-C Saúde', 51, 40.6512, -7.9123),
    ('M R Jesus-Int V Fontes', 52, 40.6525, -7.911),
    ('Quinta do Galo 1', 53, 40.653, -7.912),
    ('Quinta da Alagoa', 54, 40.6545, -7.91),
    ('Escola Aquilino Ribeiro', 55, 40.656, -7.9085),
    ('Rei D Duarte-Hospital 2', 56, 40.6581, -7.9074),
    ('Hospital S Teotónio', 57, 40.658, -7.9068),
    ('Interface Hospital (Chegada)', 60, 40.659, -7.9057)
]


MASTER_STOP_COORDS = {}
for _s in DEFAULT_STOPS_C1 + DEFAULT_STOPS_C2:
    MASTER_STOP_COORDS[_s[0]] = (_s[2], _s[3])

PONTOS_REFERENCIA = {
    "Interface Hospital": "🏥 Hospital de São Teotónio / Interface Transportes",
    "Rei D Duarte-Hospital 1": "🏥 Próximo ao Hospital S. Teotónio",
    "Rei D Duarte-Hospital 2": "🏥 Próximo ao Hospital S. Teotónio",
    "Hospital S Teotónio": "🏥 Hospital de São Teotónio",
    "Interface Hospital (Chegada)": "🏥 Hospital de São Teotónio (Chegada)",
    "M Rita Jesus-C Saúde": "🏥 Centro de Saúde",
    "COMV 1": "🚌 Central de Camionagem / Rodoviária (COMV)",
    "COMV 2": "🚌 Central de Camionagem / Rodoviária (COMV)",
    "Dr Azeredo Perdigão 1": "🛍️ Shopping Palácio do Gelo (Acesso Norte)",
    "Dr Azeredo Perdigão 2": "🛍️ Shopping Palácio do Gelo (Acesso Norte)",
    "Quinta da Alagoa": "🛍️ Shopping Palácio do Gelo (Acesso Sul / Alagoa)",
    "Dr A Alves-C Comercial 1": "🛒 Supermercado Continente / Zona Comercial",
    "5 de Outubro 1": "🛍️ Rua Comercial 5 de Outubro",
    "5 de Outubro 2": "🛍️ Rua Comercial 5 de Outubro",
    "Residências IPV": "🎓 Residências Universitárias IPV",
    "Cidade Politécnica-IPV": "🎓 IPV - Instituto Politécnico de Viseu (Campus)",
    "C Politécnica-Escola": "🎓 IPV - Instituto Politécnico de Viseu",
    "Reg Infantaria-IPV 1": "🎖️ Regimento de Infantaria n.º 14 / IPV",
    "Reg Infantaria-IPV 2": "🎖️ Regimento de Infantaria n.º 14 / IPV",
    "Reg Infantaria-IPV 3": "🎖️ Regimento de Infantaria n.º 14 / IPV",
    "Reg Infantaria": "🎖️ Regimento de Infantaria n.º 14",
    "Universidade Católica": "🎓 Universidade Católica Portuguesa",
    "Escola Viriato 2": "🏫 Escola Secundária Viriato",
    "Escola Grão Vasco": "🏫 Escola Básica 2,3 Grão Vasco",
    "Escola João de Barros 1": "🏫 Escola Básica João de Barros",
    "Escola João de Barros 2": "🏫 Escola Básica João de Barros",
    "Escola Aquilino Ribeiro": "🏫 Escola Secundária Aquilino Ribeiro",
    "Colégio Imac Conceição": "🏫 Colégio da Imaculada Conceição",
    "25 Abril-Liceu 1": "🏫 Escola Secundária Alves Martins (Liceu)",
    "25 Abril-Liceu 2": "🏫 Escola Secundária Alves Martins (Liceu)",
    "Alves Martins": "🏫 Escola Secundária Alves Martins (Liceu)",
    "Madre Rita de Jesus 1": "🏫 Escola Madre Rita de Jesus",
    "M Rita Jesus-Escola 1": "🏫 Escola Madre Rita de Jesus",
    "Biblioteca-Loja Cidadão": "🏛️ Loja do Cidadão & Biblioteca Municipal",
    "Av Europa-Tribunal 1": "⚖️ Tribunal Judicial de Viseu / Av. da Europa",
    "Av Europa-Tribunal 2": "⚖️ Tribunal Judicial de Viseu / Av. da Europa",
    "Avenida Europa": "⚖️ Tribunal Judicial de Viseu",
    "Bombeiros Voluntários": "🚒 Quartel dos Bombeiros Voluntários",
    "10 de Junho-Cemitério 1": "🪦 Cemitério Municipal de Viseu",
    "10 de Junho-Cemitério 2": "🪦 Cemitério Municipal de Viseu",
    "Cap S Pereira-Fontelo": "🌲 Parque do Fontelo",
    "Monte Belo-Estádio 1": "⚽ Estádio Municipal do Fontelo",
    "Monte Belo-Estádio 2": "⚽ Estádio Municipal do Fontelo",
    "Rossio 1": "🌳 Praça da República (Rossio) / Centro Histórico",
    "Rossio 2": "🌳 Praça da República (Rossio) / Centro Histórico",
    "Feira de S Mateus 1": "🎡 Campo de Viriato / Feira de São Mateus",
    "Feira de S. Mateus 2": "🎡 Campo de Viriato / Feira de São Mateus",
    "Fonte Cibernética 1": "⛲ Fonte Cibernética / Parque Aquilino Ribeiro",
    "Fonte Cibernética 2": "⛲ Fonte Cibernética / Parque Aquilino Ribeiro",
    "Cava de Viriato 1": "🛡️ Cava de Viriato (Monumento)",
    "Cava de Viriato 2": "🛡️ Cava de Viriato (Monumento)",
    "Porta dos Cavaleiros 1": "🏛️ Porta dos Cavaleiros / Centro Histórico",
    "Porta dos Cavaleiros 2": "🏛️ Porta dos Cavaleiros / Centro Histórico",
    "N. S. Fátima-Igreja": "⛪ Igreja de Nossa Senhora de Fátima",
    "Rua Seminário": "⛪ Seminário Maior de Viseu",
    "Paulo VI-25 Abril": "⛪ Colégio Via Sacra / Av. Paulo VI",
    "Cap S Pereira-S Cristina": "⛪ Capela de Santa Cristina",
    "S Cristina-Cap S Pereira": "⛪ Capela de Santa Cristina",
    "Largo Santo António": "⛪ Largo de Santo António",
    "Engrácia Carrilho-Igreja": "⛪ Igreja Engrácia Carrilho",
    "J Maria Escrivá-Hotel 1": "🏨 Zona Hoteleira",
    "J Maria Escrivá-Hotel 2": "🏨 Zona Hoteleira",
}

def format_stop_label(stop_name):
    ref = PONTOS_REFERENCIA.get(stop_name)
    if ref:
        return f"{stop_name} — {ref}"
    return stop_name


# --- PERSISTENCE HELPERS ---
def load_persisted_data():
    """Carrega dados persistidos; ficheiros inválidos não interrompem a aplicação."""
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        return data
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def save_persisted_data():
    """Guarda os dados de forma atómica para evitar JSON truncado."""
    data = {
        "schema_version": 1,
        "stops_c1": st.session_state.get("stops_c1", DEFAULT_STOPS_C1),
        "stops_c2": st.session_state.get("stops_c2", DEFAULT_STOPS_C2),
        "dep_dias_c1": st.session_state.get("dep_dias_c1", DEFAULT_DEPARTURES_DIAS_UTEIS),
        "dep_sab_c1": st.session_state.get("dep_sab_c1", DEFAULT_DEPARTURES_SABADOS),
        "dep_dom_c1": st.session_state.get("dep_dom_c1", DEFAULT_DEPARTURES_DOMINGOS),
        "dep_dias_c2": st.session_state.get("dep_dias_c2", DEFAULT_DEPARTURES_DIAS_UTEIS),
        "dep_sab_c2": st.session_state.get("dep_sab_c2", DEFAULT_DEPARTURES_SABADOS),
        "dep_dom_c2": st.session_state.get("dep_dom_c2", DEFAULT_DEPARTURES_DOMINGOS),
        "favorites": st.session_state.get("favorites", []),
        "version_date": st.session_state.get("version_date", DEFAULT_VERSION_DATE),
        "version_label": st.session_state.get("version_label", DEFAULT_VERSION_LABEL),
    }
    temp_file = CACHE_FILE + ".tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_file, CACHE_FILE)
    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass

# --- INITIALIZE SESSION STATE ---
cached = load_persisted_data()
if cached:
    if "stops_c1" not in st.session_state: st.session_state["stops_c1"] = [tuple(x) for x in cached.get("stops_c1", DEFAULT_STOPS_C1)]
    if "stops_c2" not in st.session_state: st.session_state["stops_c2"] = [tuple(x) for x in cached.get("stops_c2", DEFAULT_STOPS_C2)]
    if "dep_dias_c1" not in st.session_state: st.session_state["dep_dias_c1"] = cached.get("dep_dias_c1", DEFAULT_DEPARTURES_DIAS_UTEIS)
    if "dep_sab_c1" not in st.session_state: st.session_state["dep_sab_c1"] = cached.get("dep_sab_c1", DEFAULT_DEPARTURES_SABADOS)
    if "dep_dias_c2" not in st.session_state: st.session_state["dep_dias_c2"] = cached.get("dep_dias_c2", DEFAULT_DEPARTURES_DIAS_UTEIS)
    if "dep_sab_c2" not in st.session_state: st.session_state["dep_sab_c2"] = cached.get("dep_sab_c2", DEFAULT_DEPARTURES_SABADOS)
    if "dep_dom_c1" not in st.session_state: st.session_state["dep_dom_c1"] = cached.get("dep_dom_c1", DEFAULT_DEPARTURES_DOMINGOS)
    if "dep_dom_c2" not in st.session_state: st.session_state["dep_dom_c2"] = cached.get("dep_dom_c2", DEFAULT_DEPARTURES_DOMINGOS)
    if "favorites" not in st.session_state: st.session_state["favorites"] = cached.get("favorites", [])
    if "version_date" not in st.session_state: st.session_state["version_date"] = cached.get("version_date", DEFAULT_VERSION_DATE)
    if "version_label" not in st.session_state: st.session_state["version_label"] = cached.get("version_label", DEFAULT_VERSION_LABEL)
else:
    if "stops_c1" not in st.session_state: st.session_state["stops_c1"] = DEFAULT_STOPS_C1
    if "stops_c2" not in st.session_state: st.session_state["stops_c2"] = DEFAULT_STOPS_C2
    if "dep_dias_c1" not in st.session_state: st.session_state["dep_dias_c1"] = DEFAULT_DEPARTURES_DIAS_UTEIS
    if "dep_sab_c1" not in st.session_state: st.session_state["dep_sab_c1"] = DEFAULT_DEPARTURES_SABADOS
    if "dep_dom_c1" not in st.session_state: st.session_state["dep_dom_c1"] = DEFAULT_DEPARTURES_DOMINGOS
    if "dep_dias_c2" not in st.session_state: st.session_state["dep_dias_c2"] = DEFAULT_DEPARTURES_DIAS_UTEIS
    if "dep_sab_c2" not in st.session_state: st.session_state["dep_sab_c2"] = DEFAULT_DEPARTURES_SABADOS
    if "dep_dom_c2" not in st.session_state: st.session_state["dep_dom_c2"] = DEFAULT_DEPARTURES_DOMINGOS
    if "favorites" not in st.session_state: st.session_state["favorites"] = []
    if "version_date" not in st.session_state: st.session_state["version_date"] = DEFAULT_VERSION_DATE
    if "version_label" not in st.session_state: st.session_state["version_label"] = DEFAULT_VERSION_LABEL

# --- PARSER FUNCTION FOR PDF UPLOAD ---
MONTH_MAP = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'marco': 3, 'abril': 4,
    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8, 'setembro': 9,
    'outubro': 10, 'novembro': 11, 'dezembro': 12
}

def extract_version_date_from_text(text):
    match = re.search(r'EM\s+VIGOR\s+A\s+PARTIR\s+DE\s+(\d{1,2})\s+DE\s+([A-Za-zçãõÇÃÕ]+)\s+DE\s+(\d{4})', text, re.IGNORECASE)
    if match:
        day = int(match.group(1))
        month_str = match.group(2).lower()
        year = int(match.group(3))
        month = MONTH_MAP.get(month_str, 3)
        return date(year, month, day), f"{day} de {month_str.capitalize()} de {year}"
    
    match_iso = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if match_iso:
        y, m, d = map(int, match_iso.groups())
        return date(y, m, d), f"{d}/{m}/{y}"
        
    return None, None

def parse_pdf_schedules(pdf_file):
    """Extrai metadados sem inventar datas, paragens ou minutos de percurso.

    Os PDFs MUV podem ter tabelas com várias colunas de viagens. Sem uma
    estrutura inequívoca, a importação é bloqueada para evitar corromper dados.
    """
    parsed_line = None
    parsed_stops = []
    parsed_departures = []
    full_text_parts = []

    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                full_text_parts.append(page.extract_text() or "")
                if parsed_line is None:
                    page_text = full_text_parts[-1]
                    line_match = re.search(r"\\b(?:LINHA\\s*)?(C[12])\\b", page_text, re.IGNORECASE)
                    if line_match:
                        parsed_line = line_match.group(1).upper()
        full_text = "\\n".join(full_text_parts)
    except Exception:
        return None, [], [], None, None

    pdf_date_obj, pdf_date_label = extract_version_date_from_text(full_text)

    # Do not interpret every clock value in a PDF as a terminal departure:
    # these values may represent intermediate stops or notes.
    return parsed_line, parsed_stops, parsed_departures, pdf_date_obj, pdf_date_label

# --- HELPER FUNCTIONS ---
def str_to_time_delta(time_str: str) -> timedelta:
    h, m = map(int, time_str.split(":"))
    return timedelta(hours=h, minutes=m)

def format_timedelta(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"

def calculate_next_trips(line_code, tipo_dia, orig_stop, dest_stop, ref_time_obj, n_results):
    stops_list = st.session_state["stops_c1"] if line_code == "C1" else st.session_state["stops_c2"]
    
    if line_code == "C1":
        if tipo_dia == "Dias Úteis":
            departures_base = st.session_state["dep_dias_c1"]
        elif tipo_dia == "Sábados":
            departures_base = st.session_state["dep_sab_c1"]
        else:
            departures_base = st.session_state["dep_dom_c1"]
    else:
        if tipo_dia == "Dias Úteis":
            departures_base = st.session_state["dep_dias_c2"]
        elif tipo_dia == "Sábados":
            departures_base = st.session_state["dep_sab_c2"]
        else:
            departures_base = st.session_state["dep_dom_c2"]

    stop_dict = {name: offset for name, offset, lat, lon in stops_list}
    if orig_stop not in stop_dict or dest_stop not in stop_dict:
        return [], False

    orig_offset = stop_dict[orig_stop]
    dest_offset = stop_dict[dest_stop]

    if dest_offset >= orig_offset:
        duration_min = dest_offset - orig_offset
        via_terminal = False
    else:
        duration_min = (60 - orig_offset) + dest_offset
        via_terminal = True

    ref_td = timedelta(hours=ref_time_obj.hour, minutes=ref_time_obj.minute)

    results = []
    for dep_str in departures_base:
        try:
            base_td = str_to_time_delta(dep_str)
        except (TypeError, ValueError):
            continue
        if base_td < timedelta(0) or base_td >= timedelta(days=1):
            continue
        orig_time_td = base_td + timedelta(minutes=orig_offset)
        dest_time_td = orig_time_td + timedelta(minutes=duration_min)

        if orig_time_td >= ref_td:
            diff_minutes = int((orig_time_td.total_seconds() - ref_td.total_seconds()) // 60)
            if diff_minutes == 0:
                faltam_str = "A sair agora"
            elif diff_minutes < 60:
                faltam_str = f"Faltam {diff_minutes} min"
            else:
                h = diff_minutes // 60
                m = diff_minutes % 60
                faltam_str = f"Faltam {h}h{m:02d}m"

            dur_label = f"{duration_min} min"
            if via_terminal:
                dur_label += " (via Terminal)"

            results.append({
                "Partida da Origem": format_timedelta(orig_time_td),
                "Chegada ao Destino": format_timedelta(dest_time_td),
                "Tempo Restante": faltam_str,
                "Duração Estimada": dur_label,
                "Saída Terminal": dep_str,
                "Duração Minutos": duration_min,
                "Chegada TD": dest_time_td,
                "Partida TD": orig_time_td
            })
            if len(results) == n_results:
                break

    return results, True

def create_pdf_report(line_code, tipo_dia, orig_stop, dest_stop, trips):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"MUV Viseu - Consulta de Horarios ({line_code})", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(5)
    
    pdf.cell(0, 7, f"Regime: {tipo_dia}", ln=True)
    pdf.cell(0, 7, f"Origem: {orig_stop}", ln=True)
    pdf.cell(0, 7, f"Destino: {dest_stop}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(36, 8, "Partida Origem", border=1)
    pdf.cell(36, 8, "Chegada Destino", border=1)
    pdf.cell(36, 8, "Tempo Restante", border=1)
    pdf.cell(36, 8, "Duracao", border=1)
    pdf.cell(36, 8, "Saida Terminal", border=1, ln=True)

    pdf.set_font("Helvetica", "", 10)
    for trip in trips:
        pdf.cell(36, 8, str(trip["Partida da Origem"]), border=1)
        pdf.cell(36, 8, str(trip["Chegada ao Destino"]), border=1)
        pdf.cell(36, 8, str(trip["Tempo Restante"]), border=1)
        pdf.cell(36, 8, str(trip["Duração Estimada"]), border=1)
        pdf.cell(36, 8, str(trip["Saída Terminal"]), border=1, ln=True)

    return pdf.output()

def create_ics_calendar(line_code, orig_stop, dest_stop, trip_time_str, dest_time_str):
    """Gera evento iCalendar com viragem de dia e escape de caracteres."""
    base_date = datetime.now().date()

    def parse_clock(value):
        hours, minutes = map(int, value.split(":"))
        return datetime.combine(base_date, time.min) + timedelta(hours=hours, minutes=minutes)

    def ics_escape(value):
        slash = chr(92)
        value = str(value).replace(slash, slash + slash)
        value = value.replace(";", slash + ";").replace(",", slash + ",")
        return value.replace(chr(13), "").replace(chr(10), slash + "n")

    start_dt = parse_clock(trip_time_str)
    end_dt = parse_clock(dest_time_str)
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)

    summary = ics_escape(f"Autocarro MUV {line_code}: {orig_stop} -> {dest_stop}")
    description_text = (f"Viagem de autocarro MUV Viseu da {line_code}." + chr(10)
                        + f"Partida: {trip_time_str}" + chr(10) + f"Chegada: {dest_time_str}")
    description = ics_escape(description_text)
    location = ics_escape(f"{orig_stop}, Viseu")

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//MUV Viseu//Horarios Bus//PT
BEGIN:VEVENT
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{location}
DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}
END:VEVENT
END:VCALENDAR"""
    return ics_content.encode("utf-8")


# --- USER INTERFACE ---
st.title("🚌 MUViseu Circulares")
st.info(f"📅 **Versão dos Horários em Vigor:** {st.session_state.get('version_label', '1 de Março de 2026')} *(Fonte Oficial MUV)*")

st.markdown("Aplicação interativa em Python e Streamlit com **Comparador Inteligente C1 vs C2**, **Gestor de Favoritos**, **mapa interativo Folium**, **PDF upload**, e **exportação .ICS/PDF/CSV**.")

# Sidebar Settings
st.sidebar.header("⚙️ Parâmetros da Viagem")
st.sidebar.markdown(f"🗓️ **Versão ativa:** `{st.session_state.get('version_label', '1 de Março de 2026')}`")

modo_linha = st.sidebar.radio(
    "Escolha a Linha",
    ["⚡ Comparar C1 e C2 (Mais Rápida)", "Linha C1", "Linha C2"]
)

tipo_dia = st.sidebar.radio("Tipo de Dia", ["Dias Úteis", "Sábados", "Domingos e Feriados"])

# Get stops based on selected mode
stops_c1_names = [s[0] for s in st.session_state["stops_c1"]]
stops_c2_names = [s[0] for s in st.session_state["stops_c2"]]

if modo_linha == "Linha C1":
    available_stops = stops_c1_names
elif modo_linha == "Linha C2":
    available_stops = stops_c2_names
else:
    # Union of all stop names preserving order
    all_stops = list(dict.fromkeys(stops_c1_names + stops_c2_names))
    available_stops = all_stops

# Handle Favorite selection trigger
if "sel_origem" not in st.session_state:
    st.session_state["sel_origem"] = available_stops[0]
if "sel_destino" not in st.session_state:
    st.session_state["sel_destino"] = available_stops[min(13, len(available_stops)-1)]

# Ensure selections are valid within available_stops
if st.session_state["sel_origem"] not in available_stops:
    st.session_state["sel_origem"] = available_stops[0]
if st.session_state["sel_destino"] not in available_stops:
    st.session_state["sel_destino"] = available_stops[min(13, len(available_stops)-1)]

origem = st.sidebar.selectbox("Paragem de Origem", available_stops, format_func=format_stop_label, key="sel_origem")
destino = st.sidebar.selectbox("Paragem de Destino", available_stops, format_func=format_stop_label, key="sel_destino")

# Button to set current time
if st.sidebar.button("⏱️ Usar Hora Atual"):
    st.session_state["time_input_val"] = datetime.now().time()

initial_time = st.session_state.get("time_input_val", time(8, 0))
horario_desejado = st.sidebar.time_input("Horário Desejado a partir de", value=initial_time)
n_horarios = st.sidebar.number_input("Número de próximos horários (N)", min_value=1, max_value=10, value=3, step=1)

# FAVORITES MANAGEMENT SECTION
st.sidebar.markdown("---")
st.sidebar.header("⭐ Percursos Favoritos")

# Quick add current route
fav_label = f"{origem} ➔ {destino}"
if st.sidebar.button("⭐ Guardar este Percurso nos Favoritos"):
    new_fav = {"origem": origem, "destino": destino, "modo": modo_linha}
    if new_fav not in st.session_state["favorites"]:
        st.session_state["favorites"].append(new_fav)
        save_persisted_data()
        st.sidebar.success(f"Guardado: {fav_label}")

if st.session_state["favorites"]:
    st.sidebar.caption("Clique num favorito para carregar instantaneamente:")
    valid_favorites = [
        fav for fav in st.session_state["favorites"]
        if isinstance(fav, dict)
        and fav.get("origem") in available_stops
        and fav.get("destino") in available_stops
    ]
    st.session_state["favorites"] = valid_favorites
    for idx, fav in enumerate(st.session_state["favorites"]):
        col_f1, col_f2 = st.sidebar.columns([4, 1])
        with col_f1:
            if st.button(f"📌 {fav['origem']} ➔ {fav['destino']}", key=f"fav_btn_{idx}"):
                st.session_state["sel_origem"] = fav["origem"]
                st.session_state["sel_destino"] = fav["destino"]
                st.rerun()
        with col_f2:
            if st.button("❌", key=f"fav_del_{idx}"):
                st.session_state["favorites"].pop(idx)
                save_persisted_data()
                st.rerun()
else:
    st.sidebar.info("Nenhum percurso favorito guardado.")

# PDF UPLOADER SECTION IN SIDEBAR
st.sidebar.markdown("---")
st.sidebar.header("📂 Atualizar Dados por PDF")
uploaded_pdf = st.sidebar.file_uploader("Carregar PDF de Horários", type=["pdf"])

if uploaded_pdf is not None:
    line_parsed, new_stops, new_deps, pdf_date_obj, pdf_date_label = parse_pdf_schedules(uploaded_pdf)
    target_line = line_parsed if line_parsed else ("C1" if modo_linha != "Linha C2" else "C2")
    
    curr_date_str = st.session_state.get("version_date", DEFAULT_VERSION_DATE)
    try:
        cy, cm, cd = map(int, curr_date_str.split("-"))
        curr_date_obj = date(cy, cm, cd)
    except Exception:
        curr_date_obj = date(2026, 3, 1)

    is_newer = pdf_date_obj is not None and pdf_date_obj > curr_date_obj
    is_same = pdf_date_obj is not None and pdf_date_obj == curr_date_obj
    is_older = pdf_date_obj is not None and pdf_date_obj < curr_date_obj
    pdf_import_valid = pdf_date_obj is not None and bool(new_stops or new_deps)

    with st.sidebar.expander("🔍 Pré-visualização e Validação do PDF", expanded=True):
        st.write(f"**Linha Identificada:** {target_line}")
        st.write(f"**Data no PDF:** `{pdf_date_label or 'Não identificada'}`")
        st.write(f"**Data em Vigor na App:** `{st.session_state['version_label']}`")
        
        if pdf_date_obj is None:
            st.error("⛔ Não foi possível identificar uma data de entrada em vigor explícita. A importação foi bloqueada.")
        elif not pdf_import_valid:
            st.warning("⚠️ O PDF não contém uma estrutura de horários/paragens reconhecida com segurança. Nenhum dado será importado automaticamente.")
        elif is_older:
            st.error(f"⛔ **PDF Desatualizado!** Os horários deste PDF ({pdf_date_label}) são anteriores à versão em vigor ({st.session_state['version_label']}).")
        elif is_same:
            st.info(f"ℹ️ **Mesma Versão:** O PDF tem a mesma data da versão ativa ({pdf_date_label}).")
        else:
            st.success(f"🚀 **PDF Mais Recente!** Esta versão ({pdf_date_label}) irá atualizar a app.")

        st.write(f"**Paragens Detetadas:** {len(new_stops)}")
        st.write(f"**Horários Detetados:** {len(new_deps)}")

    if not pdf_import_valid or is_older:
        st.sidebar.warning("⚠️ Importação automática bloqueada: dados insuficientes ou PDF desatualizado.")
    else:
        if st.sidebar.button("✅ Confirmar e Importar PDF"):
            if new_stops:
                if target_line == "C1": st.session_state["stops_c1"] = new_stops
                else: st.session_state["stops_c2"] = new_stops
            if new_deps:
                if tipo_dia == "Dias Úteis": st.session_state[f"dep_dias_{target_line.lower()}"] = new_deps
                elif tipo_dia == "Sábados": st.session_state[f"dep_sab_{target_line.lower()}"] = new_deps
                else: st.session_state[f"dep_dom_{target_line.lower()}"] = new_deps
            
            st.session_state["version_date"] = str(pdf_date_obj)
            st.session_state["version_label"] = pdf_date_label
            save_persisted_data()
            st.sidebar.success(f"✅ Dados guardados! Versão ativa: {pdf_date_label}")
            st.rerun()


if st.sidebar.button("🔄 Restaurar Dados Oficiais Padrão"):
    st.session_state["stops_c1"] = DEFAULT_STOPS_C1
    st.session_state["stops_c2"] = DEFAULT_STOPS_C2
    st.session_state["dep_dias_c1"] = DEFAULT_DEPARTURES_DIAS_UTEIS
    st.session_state["dep_sab_c1"] = DEFAULT_DEPARTURES_SABADOS
    st.session_state["dep_dom_c1"] = DEFAULT_DEPARTURES_DOMINGOS
    st.session_state["dep_dias_c2"] = DEFAULT_DEPARTURES_DIAS_UTEIS
    st.session_state["dep_sab_c2"] = DEFAULT_DEPARTURES_SABADOS
    st.session_state["dep_dom_c2"] = DEFAULT_DEPARTURES_DOMINGOS
    st.session_state["favorites"] = []
    st.session_state["version_date"] = DEFAULT_VERSION_DATE
    st.session_state["version_label"] = DEFAULT_VERSION_LABEL
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    st.sidebar.info("Dados restaurados para a versão oficial MUV mais recente em vigor: 1 de Março de 2026.")
    st.rerun()


# Main Output Layout with Tabs
tab_consultar, tab_mapa, tab_detalhes = st.tabs([
    "🔍 Consulta & Comparador", 
    "🗺️ Mapa do Percurso", 
    "📱 Resumo Compacto / Mobile"
])

# Sempre inicializadas: a vista mobile também é renderizada quando origem == destino.
trips_c1, trips_c2 = [], []
best_line = None

with tab_consultar:
    st.subheader(f"📍 Percurso: {origem} ➔ {destino}")
    ref_orig = PONTOS_REFERENCIA.get(origem, "")
    ref_dest = PONTOS_REFERENCIA.get(destino, "")
    if ref_orig or ref_dest:
        orig_info = f"**Origem:** {ref_orig}" if ref_orig else ""
        dest_info = f"**Destino:** {ref_dest}" if ref_dest else ""
        info_str = " | ".join([p for p in [orig_info, dest_info] if p])
        st.info(f"📍 **Pontos de Referência:** {info_str}")
    st.write(f"**Modo:** {modo_linha} | **Regime:** {tipo_dia} | **Consulta a partir de:** {horario_desejado.strftime('%H:%M')}")

    if origem == destino:
        st.warning("⚠️ A paragem de origem e de destino são idênticas. Selecione paragens diferentes.")
    else:
        # Check trips for C1 and C2
        trips_c1, valid_c1 = calculate_next_trips("C1", tipo_dia, origem, destino, horario_desejado, n_horarios)
        trips_c2, valid_c2 = calculate_next_trips("C2", tipo_dia, origem, destino, horario_desejado, n_horarios)

        if modo_linha == "⚡ Comparar C1 e C2 (Mais Rápida)":
            st.markdown("### ⚡ Comparador Inteligente: C1 vs C2")

            if not trips_c1 and not trips_c2:
                st.info("ℹ️ Não foram encontradas viagens para nenhuma das linhas com as paragens selecionadas.")
            else:
                best_line = None
                time_saved = 0
                
                # Determine arrival times for comparison
                arr_c1 = trips_c1[0]["Chegada TD"] if trips_c1 else None
                arr_c2 = trips_c2[0]["Chegada TD"] if trips_c2 else None
                
                if arr_c1 and arr_c2:
                    diff_min = int(abs((arr_c1 - arr_c2).total_seconds()) // 60)
                    if arr_c1 < arr_c2:
                        best_line = "C1"
                        time_saved = diff_min
                    elif arr_c2 < arr_c1:
                        best_line = "C2"
                        time_saved = diff_min
                    else:
                        best_line = "Empate"
                elif arr_c1:
                    best_line = "C1"
                elif arr_c2:
                    best_line = "C2"

                # Recommendation Banner
                if best_line in ["C1", "C2"]:
                    rec_trip = trips_c1[0] if best_line == "C1" else trips_c2[0]
                    saved_msg = f" — chega {time_saved} minuto(s) mais cedo!" if time_saved > 0 else "!"
                    st.success(
                        f"🚀 **RECOMENDAÇÃO IDEAL:** Apanhe a **Linha {best_line}** com partida às **{rec_trip['Partida da Origem']}** "
                        f"e chegada às **{rec_trip['Chegada ao Destino']}**{saved_msg}"
                    )
                elif best_line == "Empate":
                    st.info("🤝 **EMPATE:** Ambas as linhas C1 e C2 chegam ao destino exatamente no mesmo horário!")

                # Side by side view for C1 and C2
                col_c1, col_c2 = st.columns(2)

                with col_c1:
                    st.markdown("#### 🚌 Linha C1 (Circular)")
                    if trips_c1:
                        st.metric("Próxima Chegada", trips_c1[0]["Chegada ao Destino"], delta=f"Partida: {trips_c1[0]['Partida da Origem']}")
                        st.dataframe(pd.DataFrame(trips_c1)[["Partida da Origem", "Chegada ao Destino", "Tempo Restante", "Duração Estimada"]], use_container_width=True)
                    else:
                        st.warning("Sem rotas na C1 para estas paragens.")

                with col_c2:
                    st.markdown("#### 🚌 Linha C2 (Circular)")
                    if trips_c2:
                        st.metric("Próxima Chegada", trips_c2[0]["Chegada ao Destino"], delta=f"Partida: {trips_c2[0]['Partida da Origem']}")
                        st.dataframe(pd.DataFrame(trips_c2)[["Partida da Origem", "Chegada ao Destino", "Tempo Restante", "Duração Estimada"]], use_container_width=True)
                    else:
                        st.warning("Sem rotas na C2 para estas paragens.")

        else:
            # Single Line Mode (C1 or C2)
            active_line = "C1" if modo_linha == "Linha C1" else "C2"
            trips = trips_c1 if active_line == "C1" else trips_c2

            if not trips:
                st.info("ℹ️ Não foram encontrados horários disponíveis para o dia/paragens selecionados.")
            else:
                df_trips = pd.DataFrame(trips)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(label="🚌 Próxima Partida", value=trips[0]["Partida da Origem"])
                with col2:
                    st.metric(label="⏳ Tempo Restante", value=trips[0]["Tempo Restante"])
                with col3:
                    st.metric(label="🏁 Chegada ao Destino", value=trips[0]["Chegada ao Destino"])
                with col4:
                    st.metric(label="⏱️ Duração Viagem", value=trips[0]["Duração Estimada"])

                st.markdown(f"### 📋 Próximos {len(trips)} Horários - Linha {active_line}")
                st.dataframe(df_trips[["Partida da Origem", "Chegada ao Destino", "Tempo Restante", "Duração Estimada", "Saída Terminal"]], use_container_width=True)

                # Export Section
                st.markdown("#### 📥 Exportação de Resultados & Lembretes")
                exp_col1, exp_col2, exp_col3 = st.columns(3)

                with exp_col1:
                    csv_data = df_trips[["Partida da Origem", "Chegada ao Destino", "Tempo Restante", "Duração Estimada", "Saída Terminal"]].to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📄 Descarregar Tabela em CSV",
                        data=csv_data,
                        file_name=f"horarios_{active_line}_{origem}_para_{destino}.csv",
                        mime="text/csv"
                    )

                with exp_col2:
                    try:
                        pdf_bytes = create_pdf_report(active_line, tipo_dia, origem, destino, trips)
                        st.download_button(
                            label="📕 Descarregar Relatório PDF",
                            data=bytes(pdf_bytes),
                            file_name=f"relatorio_horarios_{active_line}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Erro ao gerar PDF: {e}")

                with exp_col3:
                    ics_data = create_ics_calendar(
                        active_line, origem, destino, 
                        trips[0]["Partida da Origem"], trips[0]["Chegada ao Destino"]
                    )
                    st.download_button(
                        label="📅 Adicionar Lembrete (.ICS)",
                        data=ics_data,
                        file_name=f"lembrete_autocarro_{active_line}.ics",
                        mime="text/calendar"
                    )

with tab_mapa:
    st.subheader("🗺️ Mapa do Percurso Urbano")
    
    # Build master map of all stop names -> (lat, lon)
    all_stops_dict = {}
    for s_name, s_off, s_lat, s_lon in st.session_state["stops_c1"] + st.session_state["stops_c2"]:
        all_stops_dict[s_name] = (s_lat, s_lon)

    orig_raw_coords = all_stops_dict.get(origem)
    dest_raw_coords = all_stops_dict.get(destino)

    stops_c1_names = [s[0] for s in st.session_state["stops_c1"]]
    stops_c2_names = [s[0] for s in st.session_state["stops_c2"]]

    c1_has_orig = origem in stops_c1_names
    c1_has_dest = destino in stops_c1_names
    c2_has_orig = origem in stops_c2_names
    c2_has_dest = destino in stops_c2_names

    # Automatic selection of default line for map
    if c1_has_orig and c1_has_dest and not (c2_has_orig and c2_has_dest):
        auto_line = "C1"
    elif c2_has_orig and c2_has_dest and not (c1_has_orig and c1_has_dest):
        auto_line = "C2"
    elif c1_has_orig:
        auto_line = "C1"
    elif c2_has_orig:
        auto_line = "C2"
    elif modo_linha == "Linha C2":
        auto_line = "C2"
    else:
        auto_line = "C1"

    col_map_line, col_map_style = st.columns([1, 1])
    with col_map_line:
        target_map_line = st.radio(
            "Escolha a Linha para Visualizar no Mapa:",
            ["C1", "C2"],
            index=0 if auto_line == "C1" else 1,
            horizontal=True,
            key="map_line_select"
        )
            
    with col_map_style:
        estilo_mapa = st.selectbox(
            "🗺️ Escolha o Estilo de Visualização do Mapa",
            [
                "🗺️ Esri WorldStreetMap (Detalhado Estilo Google Maps)",
                "🌿 OpenStreetMap Standard (Oficial)",
                "🏖️ OpenStreetMap HOT (Alta Visibilidade & Cores)",
                "🛰️ Esri Satélite (Visão Aérea / Fotografia Real)"
            ],
            index=0,
            key="map_style_select"
        )
    
    p_str = "https://"
    tile_providers = {
        "🗺️ Esri WorldStreetMap (Detalhado Estilo Google Maps)": (
            p_str + "server." + "arcgisonline" + ".com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            "Esri — Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, METI, TomTom, 2012"
        ),
        "🌿 OpenStreetMap Standard (Oficial)": (
            p_str + "tile.openstreetmap.org/{z}/{x}/{y}.png",
            "&copy; OpenStreetMap contributors"
        ),
        "🏖️ OpenStreetMap HOT (Alta Visibilidade & Cores)": (
            p_str + "a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
            "&copy; OpenStreetMap contributors, HOT style"
        ),
        "🛰️ Esri Satélite (Visão Aérea / Fotografia Real)": (
            p_str + "server." + "arcgisonline" + ".com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP"
        )
    }
    
    tile_url, tile_attr = tile_providers.get(
        estilo_mapa, 
        tile_providers["🗺️ Esri WorldStreetMap (Detalhado Estilo Google Maps)"]
    )
    
    map_stops = st.session_state["stops_c1"] if target_map_line == "C1" else st.session_state["stops_c2"]
    stop_names_list = [s[0] for s in map_stops]
    
    # Detect if Origem and Destino have identical or near-identical coordinates (< 15 meters)
    is_overlapping = False
    if orig_raw_coords and dest_raw_coords and origem != destino:
        lat_diff = abs(orig_raw_coords[0] - dest_raw_coords[0])
        lon_diff = abs(orig_raw_coords[1] - dest_raw_coords[1])
        if lat_diff < 0.0025 and lon_diff < 0.0025:
            is_overlapping = True

    if is_overlapping and orig_raw_coords and dest_raw_coords:
        orig_display_lat = orig_raw_coords[0] - 0.0007
        orig_display_lon = orig_raw_coords[1] - 0.0007
        dest_display_lat = dest_raw_coords[0] + 0.0007
        dest_display_lon = dest_raw_coords[1] + 0.0007
        st.info(f"🟢 **Origem ({origem})** e 🔴 **Destino ({destino})** com separação visual aplicada no mapa para exibição dos dois marcadores lado a lado.")
    else:
        orig_display_lat, orig_display_lon = orig_raw_coords if orig_raw_coords else (40.6600, -7.9120)
        dest_display_lat, dest_display_lon = dest_raw_coords if dest_raw_coords else (40.6600, -7.9120)

    # Initialize Folium Map
    m = folium.Map(
        location=[40.6600, -7.9120], 
        zoom_start=14, 
        tiles=tile_url, 
        attr=tile_attr
    )

    # Collect points to auto-fit map bounds
    fit_points = [[s[2], s[3]] for s in map_stops]
    if orig_raw_coords: fit_points.append([orig_raw_coords[0], orig_raw_coords[1]])
    if dest_raw_coords: fit_points.append([dest_raw_coords[0], dest_raw_coords[1]])

    lats = [p[0] for p in fit_points]
    lons = [p[1] for p in fit_points]
    if lats and lons:
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=(25, 25))
    
    # 1. Full Line Circuit Path (Solid Blue)
    full_path_coords = [[s[2], s[3]] for s in map_stops]
    folium.PolyLine(
        full_path_coords,
        color="#0066FF",
        weight=4,
        opacity=0.75,
        tooltip=f"Circuito Completo da Linha {target_map_line}"
    ).add_to(m)

    # 2. Highlighted Travel Segment (Origem -> Destino) in bold RED
    has_orig = origem in stop_names_list
    has_dest = destino in stop_names_list

    if has_orig and has_dest and origem != destino:
        orig_idx = stop_names_list.index(origem)
        dest_idx = stop_names_list.index(destino)
        
        if dest_idx > orig_idx:
            sub_stops = map_stops[orig_idx : dest_idx + 1]
        elif dest_idx < orig_idx:
            sub_stops = map_stops[orig_idx:] + map_stops[: dest_idx + 1]
        else:
            sub_stops = [map_stops[orig_idx]]

        sub_coords = [[s[2], s[3]] for s in sub_stops]
        if len(sub_coords) >= 2:
            folium.PolyLine(
                sub_coords,
                color="#FF0000",
                weight=8,
                opacity=0.95,
                tooltip=f"🚀 Percurso Selecionado: {origem} ➔ {destino}"
            ).add_to(m)
            st.success(f"📍 **Percurso Destacado a Vermelho:** {origem} ➔ {destino} (Linha {target_map_line})")
    elif (has_orig or has_dest) and orig_raw_coords and dest_raw_coords and origem != destino:
        folium.PolyLine(
            [[orig_display_lat, orig_display_lon], [dest_display_lat, dest_display_lon]],
            color="#FF0000",
            weight=6,
            opacity=0.9,
            dash_array="8, 8",
            tooltip=f"🚀 Percurso entre Linhas: {origem} ➔ {destino}"
        ).add_to(m)
        st.info(f"📍 **Percurso entre Linhas:** {origem} ➔ {destino}. (Linha ativa: {target_map_line}).")

    if is_overlapping:
        folium.PolyLine(
            [[orig_display_lat, orig_display_lon], [dest_display_lat, dest_display_lon]],
            color="#666666",
            weight=3,
            dash_array="4, 4",
            tooltip=f"Ligação de Proximidade: {origem} / {destino}"
        ).add_to(m)

    # 3. Render Intermediate Stop Markers
    for s_name, s_off, s_lat, s_lon in map_stops:
        if s_name != origem and s_name != destino:
            ref_text = PONTOS_REFERENCIA.get(s_name, "")
            ref_label = f"<br><small>{ref_text}</small>" if ref_text else ""
            popup_html = f"<div style='font-family:sans-serif;'><b>🚌 Paragem: {s_name}</b>{ref_label}</div>"
            folium.CircleMarker(
                location=[s_lat, s_lon],
                radius=5,
                color="#0044AA",
                fill=True,
                fill_color="#3399FF",
                fill_opacity=0.85,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"🚌 Paragem: {s_name}"
            ).add_to(m)

    # 4. Render ORIGEM (Green) and DESTINO (Red) Markers explicitly
    if orig_raw_coords:
        ref_text = PONTOS_REFERENCIA.get(origem, "")
        ref_label = f"<br><small>{ref_text}</small>" if ref_text else ""
        icon = folium.Icon(color="green", icon="play", prefix="fa")
        popup_html = f"<div style='font-family:sans-serif;'><b>🟢 ORIGEM: {origem}</b>{ref_label}</div>"
        folium.Marker(
            location=[orig_display_lat, orig_display_lon],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"🟢 Origem: {origem}",
            icon=icon,
            z_index_offset=2500
        ).add_to(m)

    if dest_raw_coords and origem != destino:
        ref_text = PONTOS_REFERENCIA.get(destino, "")
        ref_label = f"<br><small>{ref_text}</small>" if ref_text else ""
        icon = folium.Icon(color="red", icon="flag", prefix="fa")
        popup_html = f"<div style='font-family:sans-serif;'><b>🔴 DESTINO: {destino}</b>{ref_label}</div>"
        folium.Marker(
            location=[dest_display_lat, dest_display_lon],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"🔴 Destino: {destino}",
            icon=icon,
            z_index_offset=2000
        ).add_to(m)

    st_html(m.get_root().render(), height=540)
    st.caption("🟢 Verde: Paragem de Origem | 🔴 Vermelho: Paragem de Destino | ➖🔴 Linha Vermelha: Percurso Selecionado | ➖🔵 Linha Azul: Circuito Completo")


with tab_detalhes:
    st.subheader("📱 Visão Mobile Compacta")
    st.markdown("Visualização otimizada em cartões interativos para ecrãs de smartphone.")
    
    if modo_linha == "⚡ Comparar C1 e C2 (Mais Rápida)" and best_line in ("C1", "C2"):
        active_line_name = best_line
        active_trips = trips_c1 if best_line == "C1" else trips_c2
    elif modo_linha == "Linha C2":
        active_line_name, active_trips = "C2", trips_c2
    else:
        active_line_name, active_trips = "C1", trips_c1
    
    if origem != destino and active_trips:
        st.write(f"**Exibindo viagem na Linha {active_line_name}:**")
        for idx, trip in enumerate(active_trips, 1):
            with st.expander(f"🚌 Opção #{idx}: {trip['Partida da Origem']} ➔ {trip['Chegada ao Destino']} ({trip['Tempo Restante']})", expanded=(idx==1)):
                st.write(f"• **Partida ({origem}):** {trip['Partida da Origem']}")
                st.write(f"• **Chegada ({destino}):** {trip['Chegada ao Destino']}")
                st.write(f"• **Tempo Restante:** {trip['Tempo Restante']}")
                st.write(f"• **Duração do Percurso:** {trip['Duração Estimada']}")
                st.write(f"• **Partida do Terminal:** {trip['Saída Terminal']}")

st.markdown("---")
st.caption("MUViseu Circulares v19 - Sistema Inteligente de Horários & Mobilidade Urbana de Viseu.")
