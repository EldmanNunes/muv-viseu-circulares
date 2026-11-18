import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time, date
import re
import io
import unicodedata
from fpdf import FPDF
import json
import os
import pdfplumber
import folium
from streamlit.components.v1 import html as st_html

# --- OPENPYXL IMPORTS FOR EXCEL CONVERSION AND READING ---
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

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
    ("Interface Hospital", 0, 40.6582, -7.9065),
    ("Rei D Duarte-Hospital 1", 1, 40.6575, -7.9080),
    ("Quinta D´el Rei", 2, 40.6560, -7.9090),
    ("Dr A Alves-C Comercial 1", 3, 40.6545, -7.9105),
    ("Quinta do Galo 2", 4, 40.6536, -7.9114),
    ("Quinta de Jugueiros", 5, 40.6515, -7.9135),
    ("Residências IPV", 6, 40.6495, -7.9150),
    ("Rua Nova", 7, 40.6480, -7.9160),
    ("Cidade Politécnica-IPV", 8, 40.6465, -7.9170),
    ("Reg Infantaria-IPV 1", 9, 40.6485, -7.9180),
    ("Reg Infantaria-IPV 2", 10, 40.6506, -7.9179),
    ("Paulo VI-25 Abril", 11, 40.6520, -7.9150),
    ("25 Abril-Liceu 2", 12, 40.6546, -7.9124),
    ("Rossio 2", 13, 40.6574, -7.9122),
    ("Alberto Sampaio 1", 14, 40.6580, -7.9110),
    ("Alberto Sampaio 2", 15, 40.6596, -7.9089),
    ("N. S. Fátima-Igreja", 16, 40.6605, -7.9080),
    ("J Maria Escrivá-Hotel 2", 17, 40.6626, -7.9064),
    ("José Maria Escrivá 2", 18, 40.6641, -7.9054),
    ("Monte Belo-J Infância 1", 19, 40.6650, -7.9050),
    ("Monte Belo-Estádio 1", 20, 40.6665, -7.9040),
    ("Campo dos Trambelos", 21, 40.6680, -7.9030),
    ("Balsa 1", 22, 40.6690, -7.9020),
    ("César Anjo 1", 23, 40.6700, -7.9010),
    ("Bombeiros Voluntários", 24, 40.6685, -7.9080),
    ("COMV 1", 25, 40.6670, -7.9120),
    ("Fonte Cibernética 2", 26, 40.6666, -7.9144),
    ("Av Europa-Tribunal 2", 27, 40.6656, -7.9174),
    ("M Ferreira Figueiredo 1", 30, 40.6680, -7.9220),
    ("Pedro Henriques 1", 31, 40.6700, -7.9240),
    ("Escola Viriato 2", 33, 40.6726, -7.9254),
    ("Estrada Velha Abraveses", 35, 40.6740, -7.9280),
    ("Cava de Viriato 2", 37, 40.6656, -7.9124),
    ("Feira de S. Mateus 2", 38, 40.6626, -7.9129),
    ("Porta dos Cavaleiros 1", 39, 40.6595, -7.9125),
    ("Mouzinho de Albuquerque", 40, 40.6580, -7.9140),
    ("Capitão Silva Pereira", 41, 40.6570, -7.9155),
    ("Cap S Pereira-S Cristina", 42, 40.6560, -7.9165),
    ("5 de Outubro 1", 43, 40.6550, -7.9150),
    ("Rua Seminário", 44, 40.6540, -7.9135),
    ("Dr Azeredo Perdigão 1", 45, 40.6550, -7.9120),
    ("General Humberto Delgado", 46, 40.6560, -7.9125),
    ("Rossio 1", 48, 40.6570, -7.9126),
    ("25 Abril-Liceu 1", 50, 40.6542, -7.9128),
    ("Nuno Alvares Pereira", 51, 40.6525, -7.9140),
    ("Escola João de Barros 1", 52, 40.6510, -7.9130),
    ("Manuel Silva Almeida 1", 53, 40.6500, -7.9120),
    ("Paulo VI-25 Abril (Regresso)", 54, 40.6528, -7.9142),
    ("Escola Grão Vasco", 55, 40.6535, -7.9110),
    ("Alexandre Lucena e Vale", 56, 40.6550, -7.9090),
    ("10 de Junho-Cemitério 1", 57, 40.6565, -7.9075),
    ("Rei D Duarte-Mesuras", 58, 40.6575, -7.9070),
    ("Hospital S Teotónio", 58, 40.6580, -7.9068),
    ("Interface Hospital (Chegada)", 60, 40.6584, -7.9063)
]

DEFAULT_STOPS_C2 = [
    ("Interface Hospital", 0, 40.6582, -7.9065),
    ("Biblioteca-Loja Cidadão", 1, 40.6570, -7.9080),
    ("10 de Junho-Cemitério 2", 2, 40.6571, -7.9069),
    ("Rua Mendonça", 3, 40.6550, -7.9090),
    ("Escola Grão Vasco", 3, 40.6535, -7.9110),
    ("Praça de Goa", 4, 40.6520, -7.9120),
    ("Estevão Lopes Morago 1", 5, 40.6510, -7.9125),
    ("Manuel Silva Almeida 2", 6, 40.6506, -7.9114),
    ("Escola João de Barros 2", 7, 40.6516, -7.9124),
    ("António Esteves Correia", 8, 40.6525, -7.9135),
    ("25 Abril-Liceu 2", 9, 40.6546, -7.9124),
    ("Rossio 2", 10, 40.6574, -7.9122),
    ("Alves Martins", 11, 40.6575, -7.9135),
    ("Dr Azeredo Perdigão 2", 12, 40.6556, -7.9114),
    ("Monsenhor Celso T Silva", 13, 40.6545, -7.9140),
    ("Universidade Católica", 14, 40.6535, -7.9160),
    ("5 de Outubro 2", 15, 40.6556, -7.9144),
    ("S Cristina-Cap S Pereira", 16, 40.6560, -7.9165),
    ("Cap S Pereira-Fontelo", 17, 40.6575, -7.9150),
    ("Largo Santo António", 18, 40.6585, -7.9135),
    ("Porta dos Cavaleiros 2", 19, 40.6601, -7.9119),
    ("Feira de S Mateus 1", 20, 40.6620, -7.9135),
    ("Cava de Viriato 1", 21, 40.6650, -7.9130),
    ("Av Bélgica-Alf Miguel 1", 22, 40.6670, -7.9180),
    ("Avenida Bélgica 2", 23, 40.6691, -7.9194),
    ("Pedro Henriques 1", 24, 40.6700, -7.9240),
    ("Pedro Henriques 2", 25, 40.6716, -7.9244),
    ("M Ferreira Figueiredo 2", 27, 40.6686, -7.9214),
    ("Avenida Europa", 29, 40.6660, -7.9200),
    ("Av Europa-Tribunal 1", 31, 40.6650, -7.9180),
    ("Fonte Cibernética 1", 32, 40.6660, -7.9150),
    ("COMV 2", 33, 40.6676, -7.9114),
    ("César Anjo 2", 34, 40.6706, -7.9004),
    ("Balsa 2", 35, 40.6696, -7.9014),
    ("Cidade Aveiro", 36, 40.6675, -7.9030),
    ("Monte Belo-Estádio 2", 37, 40.6671, -7.9034),
    ("Monte Belo-J Infância 2", 38, 40.6656, -7.9044),
    ("José Maria Escrivá 1", 39, 40.6635, -7.9060),
    ("J Maria Escrivá-Hotel 1", 40, 40.6620, -7.9070),
    ("Engrácia Carrilho-Igreja", 41, 40.6600, -7.9085),
    ("Colégio Imac Conceição", 42, 40.6590, -7.9100),
    ("Alberto Sampaio 3", 43, 40.6580, -7.9110),
    ("Rossio 1", 44, 40.6570, -7.9126),
    ("25 Abril-Liceu 1", 45, 40.6542, -7.9128),
    ("25 Abril-Paulo VI", 45, 40.6520, -7.9150),
    ("Reg Infantaria", 46, 40.6500, -7.9185),
    ("Reg Infantaria-IPV 3", 47, 40.6485, -7.9180),
    ("C Politécnica-Escola", 48, 40.6465, -7.9170),
    ("Madre Rita de Jesus 1", 49, 40.6480, -7.9155),
    ("M Rita Jesus-Escola 1", 50, 40.6495, -7.9140),
    ("M Rita Jesus-C Saúde", 51, 40.6512, -7.9123),
    ("M R Jesus-Int V Fontes", 52, 40.6525, -7.9110),
    ("Quinta do Galo 1", 53, 40.6530, -7.9120),
    ("Quinta da Alagoa", 54, 40.6545, -7.9100),
    ("Escola Aquilino Ribeiro", 55, 40.6560, -7.9085),
    ("Rei D Duarte-Hospital 2", 56, 40.6581, -7.9074),
    ("Hospital S Teotónio", 57, 40.6580, -7.9068),
    ("Interface Hospital (Chegada)", 60, 40.6584, -7.9063)
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
    if "dep_dom_c1" not in st.session_state: st.session_state["dep_dom_c1"] = cached.get("dep_dom_c1", DEFAULT_DEPARTURES_DOMINGOS)
    if "dep_dias_c2" not in st.session_state: st.session_state["dep_dias_c2"] = cached.get("dep_dias_c2", DEFAULT_DEPARTURES_DIAS_UTEIS)
    if "dep_sab_c2" not in st.session_state: st.session_state["dep_sab_c2"] = cached.get("dep_sab_c2", DEFAULT_DEPARTURES_SABADOS)
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


# --- EXCEL IMPORTER (SCHEMA MUViseu v1) ---
EXCEL_REGIMES = {
    "Dias úteis": "dep_dias",
    "Sábados": "dep_sab",
    "Domingos e feriados": "dep_dom",
}

def _valid_stop_records(records):
    if not isinstance(records, list) or len(records) < 2:
        return False
    seen = set()
    for item in records:
        if not isinstance(item, (list, tuple)) or len(item) != 4:
            return False
        name, offset, lat, lon = item
        if not isinstance(name, str) or not name.strip() or name in seen:
            return False
        if isinstance(offset, bool) or not isinstance(offset, (int, float)) or offset < 0 or offset > 180:
            return False
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            return False
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return False
        seen.add(name)
    return True

def _valid_departures(values):
    if not isinstance(values, list) or len(values) < 2:
        return False
    parsed = []
    for value in values:
        if not isinstance(value, str) or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
            return False
        h, m = map(int, value.split(":"))
        parsed.append(h * 60 + m)
    if parsed != sorted(set(parsed)):
        return False
    return all((b - a) > 1 for a, b in zip(parsed, parsed[1:]))

def parse_excel_schedules(excel_file):
    """Lê um Excel estruturado; não infere nem completa valores em falta."""
    errors = []
    try:
        xls = pd.ExcelFile(excel_file)
        required_sheets = {"Configuração", "Paragens", "Horários"}
        if not required_sheets.issubset(set(xls.sheet_names)):
            return None, [], {}, None, ["O ficheiro deve conter as folhas Configuração, Paragens e Horários."]

        config = pd.read_excel(xls, sheet_name="Configuração", header=None)
        config_map = {}
        for _, row in config.iterrows():
            if len(row) >= 2 and pd.notna(row.iloc[0]):
                config_map[str(row.iloc[0]).strip().lower()] = row.iloc[1]

        line = str(config_map.get("linha", "")).strip().upper()
        if line not in ("C1", "C2"):
            errors.append("Configuração: Linha deve ser C1 ou C2.")

        raw_date = config_map.get("data de entrada em vigor")
        version_date = None
        if pd.notna(raw_date):
            try:
                if isinstance(raw_date, (datetime, date)):
                    version_date = raw_date.date() if isinstance(raw_date, datetime) else raw_date
                else:
                    date_text = str(raw_date).strip()
                    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text):
                        version_date = date.fromisoformat(date_text)
                    else:
                        version_date = pd.to_datetime(date_text, dayfirst=True).date()
            except Exception:
                errors.append("Configuração: data de entrada em vigor inválida.")
        else:
            errors.append("Configuração: falta a data de entrada em vigor.")

        stops_df = pd.read_excel(xls, sheet_name="Paragens")
        expected_stop_cols = {"Linha", "Nome", "Ordem", "Latitude", "Longitude"}
        if not expected_stop_cols.issubset(set(stops_df.columns)):
            errors.append("Paragens: colunas obrigatórias: Linha, Nome, Ordem, Latitude e Longitude.")
            stops = []
        else:
            stops = []
            selected = stops_df[stops_df["Linha"].astype(str).str.strip().str.upper() == line]
            for _, r in selected.iterrows():
                if pd.isna(r.get("Nome")):
                    continue
                name = str(r["Nome"]).strip()
                try:
                    order = float(r["Ordem"])
                    lat = float(r["Latitude"])
                    lon = float(r["Longitude"])
                    if not order.is_integer():
                        raise ValueError()
                    stops.append((name, int(order), lat, lon))
                except Exception:
                    errors.append(f"Paragens: dados inválidos na paragem «{name}».")
            if not _valid_stop_records(stops):
                errors.append("Paragens: são necessárias pelo menos 2 paragens válidas, sem nomes repetidos e com coordenadas/ordens válidas.")

        if "Conferência PDF" in xls.sheet_names:
            audit_df = pd.read_excel(xls, sheet_name="Conferência PDF")
            required_audit_cols = {"Nome na aplicação", "Estado"}
            if not required_audit_cols.issubset(set(audit_df.columns)):
                errors.append("Conferência PDF: faltam as colunas Nome na aplicação e Estado.")
            else:
                known_names = {item[0] for item in stops}
                for _, audit_row in audit_df.iterrows():
                    audit_name = str(audit_row.get("Nome na aplicação", "")).strip()
                    audit_state = str(audit_row.get("Estado", "")).strip().upper()
                    if audit_state != "VALIDADO":
                        errors.append(f"Conferência PDF: a paragem «{audit_name or 'sem nome'}» ainda não está validada ({audit_state or 'estado em falta'}).")
                    elif audit_name not in known_names:
                        errors.append(f"Conferência PDF: «{audit_name}» não existe na folha Paragens.")

        times_df = pd.read_excel(xls, sheet_name="Horários")
        if not {"Linha", "Regime", "Partida"}.issubset(set(times_df.columns)):
            errors.append("Horários: colunas obrigatórias: Linha, Regime e Partida.")
            departures = {}
        else:
            departures = {}
            selected = times_df[times_df["Linha"].astype(str).str.strip().str.upper() == line]
            for regime in EXCEL_REGIMES:
                values = []
                subset = selected[selected["Regime"].astype(str).str.strip().str.casefold() == regime.casefold()]
                for value in subset["Partida"].tolist():
                    if pd.isna(value):
                        continue
                    if isinstance(value, (datetime, time)):
                        value = value.strftime("%H:%M")
                    elif isinstance(value, (int, float)) and 0 <= value < 1:
                        mins = round(float(value) * 24 * 60)
                        value = f"{mins // 60:02d}:{mins % 60:02d}"
                    else:
                        value = str(value).strip()
                        if re.fullmatch(r"\d{1,2}:\d{2}:\d{2}", value):
                            value = value[:5]
                        values.append(value)
                if not _valid_departures(values):
                    errors.append(f"Horários: o regime «{regime}» deve conter pelo menos 2 partidas válidas, ordenadas e sem duplicados.")
                else:
                    departures[EXCEL_REGIMES[regime]] = values

        if errors:
            return line if line in ("C1", "C2") else None, [], {}, version_date, errors
        return line, stops, departures, version_date, []
    except Exception as exc:
        return None, [], {}, None, [f"Não foi possível ler o Excel: {exc}"]


# --- CONVERSOR DE PDF OFICIAL PARA EXCEL ---
def _pdf_time_from_cell(cell):
    match = re.search(r"(?<!\d)(?:[01]\d|2[0-3]):[0-5]\d(?!\d)", str(cell or ""))
    return match.group(0) if match else None

def _pdf_rows_for_line(pdf):
    page_data = {}
    full_text = []
    line = None
    for page in pdf.pages:
        text = page.extract_text() or ""
        full_text.append(text)
        m = re.search(r"\b(C[12])\s+CIRCULAR\s*\|\s*(DIAS ÚTEIS|SÁBADOS, DOMINGOS E FERIADOS)", text, re.I)
        if not m:
            continue
        detected_line = m.group(1).upper()
        regime_heading = "weekday" if "DIAS ÚTEIS" in m.group(2).upper() else "weekend"
        if line and line != detected_line:
            raise ValueError("O PDF contém páginas de linhas diferentes.")
        line = detected_line
        tables = page.extract_tables() or []
        if len(tables) != 1:
            raise ValueError(f"Página {regime_heading}: era esperada uma tabela de horários; foram encontradas {len(tables)}.")
        if regime_heading in page_data:
            raise ValueError(f"O PDF contém mais de uma página para o regime {regime_heading}.")
        page_data[regime_heading] = tables[0]
    if line not in ("C1", "C2") or set(page_data) != {"weekday", "weekend"}:
        raise ValueError("Não foi possível identificar inequivocamente as páginas de Dias úteis e Sábados/Domingos/Feriados.")
    return line, page_data["weekday"], page_data["weekend"], "\n".join(full_text)

def _normalise_pdf_label(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return " ".join(value.split())

def _find_terminal_rows(table):
    indexes = [i for i, row in enumerate(table) if row and _normalise_pdf_label(row[0]) == "interface hospital"]
    if len(indexes) != 2:
        raise ValueError(f"A tabela deve conter exatamente duas linhas Interface Hospital (partida e regresso); foram encontradas {len(indexes)}.")
    return indexes[0], indexes[1]

def _extract_stop_sequence(table):
    first, last = _find_terminal_rows(table)
    sequence = []
    for row in table[first:last + 1]:
        if not row or not str(row[0] or "").strip():
            continue
        sequence.append(row)
    if len(sequence) < 5:
        raise ValueError("A tabela não contém uma sequência de paragens suficiente.")
    return sequence

def convert_official_pdf_to_excel(pdf_file):
    """Converte um PDF oficial C1/C2 para o modelo Excel, assinalando divergências."""
    try:
        if hasattr(pdf_file, "seek"):
            pdf_file.seek(0)
        with pdfplumber.open(pdf_file) as pdf:
            line, weekday_table, weekend_table, full_text = _pdf_rows_for_line(pdf)

            version_date, date_label = extract_version_date_from_text(full_text)
            if not version_date:
                raise ValueError("O PDF não contém uma data explícita 'EM VIGOR A PARTIR DE'.")

            weekday_seq = _extract_stop_sequence(weekday_table)
            weekend_seq = _extract_stop_sequence(weekend_table)
            weekday_labels = [_normalise_pdf_label(r[0]) for r in weekday_seq]
            weekend_labels = [_normalise_pdf_label(r[0]) for r in weekend_seq]
            if weekday_labels != weekend_labels:
                raise ValueError("A sequência de paragens difere entre as páginas de Dias úteis e de Sábados/Domingos/Feriados.")

            weekday_departures = [_pdf_time_from_cell(c) for c in weekday_seq[0][2:]]
            weekday_departures = [v for v in weekday_departures if v]
            saturday_departures = [_pdf_time_from_cell(c) for c in weekend_seq[0][2:]]
            saturday_departures = [v for v in saturday_departures if v]

            marker_row = next((r for r in weekend_table if r and _normalise_pdf_label(r[0]) == "nome paragem"), None)
            if marker_row is None:
                raise ValueError("Não foi encontrada a linha de cabeçalho NOME PARAGEM no quadro de fim de semana.")
            marked_columns = {i for i, cell in enumerate(marker_row) if "**" in str(cell or "")}
            sunday_departures = []
            for col in sorted(marked_columns):
                if col < len(weekend_seq[0]):
                    value = _pdf_time_from_cell(weekend_seq[0][col])
                    if value:
                        sunday_departures.append(value)

            for label, values in (("Dias úteis", weekday_departures), ("Sábados", saturday_departures), ("Domingos e feriados", sunday_departures)):
                if not _valid_departures(values):
                    raise ValueError(f"Os horários extraídos para {label} são inválidos, incompletos ou não estão ordenados.")

            master = DEFAULT_STOPS_C1 if line == "C1" else DEFAULT_STOPS_C2
            master_by_name = {item[0]: item for item in master}
            used_names = set()
            base_departure = weekday_departures[0]
            bh, bm = map(int, base_departure.split(":"))
            stop_rows = []
            audit_rows = []
            unmatched = []

            for pos, row in enumerate(weekday_seq):
                pdf_name = str(row[0]).strip()
                row_time = _pdf_time_from_cell(row[2] if len(row) > 2 else None)
                if not row_time:
                    raise ValueError(f"Não foi possível calcular o tempo de percurso da paragem «{pdf_name}».")
                rh, rm = map(int, row_time.split(":"))
                pdf_offset = (rh * 60 + rm) - (bh * 60 + bm)
                if pdf_offset < 0:
                    pdf_offset += 24 * 60

                if pos == len(weekday_seq) - 1 and _normalise_pdf_label(pdf_name) == "interface hospital":
                    app_name = "Interface Hospital (Chegada)"
                elif line == "C1" and pdf_name == "Paulo VI-25 Abril" and pdf_name in used_names and "Paulo VI-25 Abril (Regresso)" in master_by_name:
                    app_name = "Paulo VI-25 Abril (Regresso)"
                else:
                    app_name = pdf_name if pdf_name in master_by_name else ""

                if app_name and app_name in master_by_name and app_name not in used_names:
                    master_item = master_by_name[app_name]
                    master_offset, lat, lon = master_item[1], master_item[2], master_item[3]
                    state = "VALIDADO" if int(master_offset) == int(pdf_offset) else "DIVERGÊNCIA_OFFSET"
                    note = "Correspondência exata com a lista da aplicação." if state == "VALIDADO" else f"Offset do PDF ({pdf_offset}) difere do offset da aplicação ({master_offset})."
                    if state == "DIVERGÊNCIA_OFFSET":
                        unmatched.append(f"{pdf_name}: offset PDF {pdf_offset} / aplicação {master_offset}")
                    used_names.add(app_name)
                    final_name = app_name
                else:
                    final_name = pdf_name
                    lat = None
                    lon = None
                    state = "SEM_COORDENADAS"
                    note = "Paragem não encontrada na lista da aplicação; inserir coordenadas verificadas na folha Paragens e validar esta linha."
                    unmatched.append(pdf_name)

                stop_rows.append([line, final_name, int(pdf_offset), lat, lon])
                audit_rows.append([line, pdf_name, final_name, pos + 1, int(pdf_offset),
                                   master_by_name[app_name][1] if app_name in master_by_name else None,
                                   state, note])

            missing_master = [item[0] for item in master if item[0] not in used_names]
            missing_master = [n for n in missing_master if n != "Interface Hospital (Chegada)"]
            if missing_master:
                for name in missing_master:
                    unmatched.append(f"Paragem da aplicação ausente no PDF: {name}")
                    audit_rows.append([line, "(não consta do PDF)", name, None, None, master_by_name[name][1], "AUSENTE_NO_PDF", "Confirmar se a paragem foi removida oficialmente."])

            wb = Workbook()
            cfg = wb.active
            cfg.title = "Configuração"
            cfg.append(["Campo", "Valor"])
            cfg.append(["Linha", line])
            cfg.append(["Data de entrada em vigor", version_date])
            cfg.append(["Documento de origem", f"PDF oficial {line} — {date_label}"])
            cfg.append(["Nota", "Horários extraídos da primeira linha Interface Hospital em cada página. A segunda linha Interface Hospital é o regresso/chegada."])
            cfg.append(["Regime de domingo", "Partidas marcadas com ** no cabeçalho do PDF; não foram inferidas por intervalos."])

            stops_ws = wb.create_sheet("Paragens")
            stops_ws.append(["Linha", "Nome", "Ordem", "Latitude", "Longitude"])
            for r in stop_rows:
                stops_ws.append(r)

            times_ws = wb.create_sheet("Horários")
            times_ws.append(["Linha", "Regime", "Partida"])
            for regime, values in (("Dias úteis", weekday_departures), ("Sábados", saturday_departures), ("Domingos e feriados", sunday_departures)):
                for value in values:
                    times_ws.append([line, regime, value])

            audit_ws = wb.create_sheet("Conferência PDF")
            audit_ws.append(["Linha", "Paragem no PDF", "Nome na aplicação", "Ordem PDF", "Offset PDF (min)", "Offset aplicação (min)", "Estado", "Observações"])
            for r in audit_rows:
                audit_ws.append(r)

            for ws in wb.worksheets:
                ws.freeze_panes = "A2"
                ws.row_dimensions[1].height = 24
                for cell in ws[1]:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill("solid", fgColor="245A73")
                    cell.alignment = Alignment(vertical="center", wrap_text=True)
                for row_cells in ws.iter_rows(min_row=2):
                    for cell in row_cells:
                        cell.alignment = Alignment(vertical="center", wrap_text=True)
                ws.auto_filter.ref = ws.dimensions
            for ws, widths in ((cfg, [34, 100]), (stops_ws, [12, 42, 14, 16, 16]), (times_ws, [12, 30, 16]), (audit_ws, [12, 34, 38, 14, 18, 22, 22, 90])):
                for col, width in enumerate(widths, 1):
                    ws.column_dimensions[get_column_letter(col)].width = width

            regime_validation = DataValidation(type="list", formula1='"Dias úteis,Sábados,Domingos e feriados"', allow_blank=False)
            times_ws.add_data_validation(regime_validation)
            regime_validation.add(f"B2:B{times_ws.max_row}")

            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            report = {
                "line": line,
                "date": version_date,
                "weekday_count": len(weekday_departures),
                "saturday_count": len(saturday_departures),
                "sunday_count": len(sunday_departures),
                "stop_count": len(stop_rows),
                "issues": unmatched,
                "audit_valid": sum(1 for r in audit_rows if r[6] == "VALIDADO"),
                "audit_pending": sum(1 for r in audit_rows if r[6] != "VALIDADO"),
            }
            return output.getvalue(), report
    except Exception as exc:
        raise RuntimeError(f"{exc}")


# --- PARSER FUNCTION FOR PDF UPLOAD ---
MONTH_MAP = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'marco': 3, 'abril': 4,
    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8, 'setembro': 9,
    'outubro': 10, 'novembro': 11, 'dezembro': 12
}

def extract_version_date_from_text(text):
    """Extrai a data de vigor do PDF sem fallbacks fictícios."""
    match = re.search(
        r'EM\s+VIGOR\s+A\s+PARTIR\s+DE\s+(\d{1,2})\s+DE\s+([A-Za-zçãõÇÃÕ]+)\s+DE\s+(\d{4})',
        text, re.IGNORECASE
    )
    if match:
        day = int(match.group(1))
        month_str = match.group(2).lower()
        year = int(match.group(3))
        month = MONTH_MAP.get(month_str)
        if month:
            return date(year, month, day), f"{day} de {month_str.capitalize()} de {year}"
    
    match_iso = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if match_iso:
        y, m, d = map(int, match_iso.groups())
        if 1 <= m <= 12 and 1 <= d <= 31:
            return date(y, m, d), f"{d}/{m}/{y}"
        
    return None, None

def parse_pdf_schedules(pdf_file):
    """Extrai linha, paragens, partidas e data de vigor de um PDF oficial MUV."""
    parsed_line = None
    parsed_stops = []
    parsed_departures = []
    full_text_parts = []

    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text_parts.append(text)
                
                # Fix P0 Regex for Line Detection: use \b(?:LINHA\s*)?(C[12])\b
                if parsed_line is None:
                    line_match = re.search(r"\b(?:LINHA\s*)?(C[12])\b", text, re.IGNORECASE)
                    if line_match:
                        parsed_line = line_match.group(1).upper()
                
                # Extract Tables for stops & departure times
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        clean_row = [c.strip() for c in row if c and c.strip()]
                        if len(clean_row) >= 2:
                            stop_candidate = clean_row[0]
                            # Detect stop rows
                            if stop_candidate in MASTER_STOP_COORDS or any(ch.isalpha() for ch in stop_candidate):
                                if stop_candidate not in [s[0] for s in parsed_stops]:
                                    offset = len(parsed_stops) * 2
                                    coords = MASTER_STOP_COORDS.get(stop_candidate, (
                                        40.6568 + len(parsed_stops)*0.0003,
                                        -7.9128 + len(parsed_stops)*0.0003
                                    ))
                                    parsed_stops.append((stop_candidate, offset, coords[0], coords[1]))
                            
                            # Detect terminal departures (Interface Hospital row)
                            if "interface hospital" in stop_candidate.lower() or "terminal" in stop_candidate.lower():
                                for cell in clean_row[1:]:
                                    times_in_cell = re.findall(r"\b(?:[01]\d|2[0-3]):[0-5]\d\b", cell)
                                    for t_str in times_in_cell:
                                        if t_str not in parsed_departures:
                                            parsed_departures.append(t_str)

        full_text = "\n".join(full_text_parts)
    except Exception:
        return None, [], [], None, None

    # Fallback to general text extraction for line if tables didn't capture it
    if parsed_line is None:
        if "C1" in full_text or "Linha C1" in full_text:
            parsed_line = "C1"
        elif "C2" in full_text or "Linha C2" in full_text:
            parsed_line = "C2"

    # Fallback to general terminal departure extraction if terminal row wasn't found
    if not parsed_departures:
        all_times = re.findall(r"\b(?:[01]\d|2[0-3]):[0-5]\d\b", full_text)
        if all_times:
            unique_times = sorted(list(set(all_times)))
            if len(unique_times) >= 5 and not has_suspicious_departure_intervals(unique_times):
                parsed_departures = unique_times

    pdf_date_obj, pdf_date_label = extract_version_date_from_text(full_text)
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

def has_suspicious_departure_intervals(departures):
    """Deteta listas provavelmente contaminadas com horas de passagem intermédias."""
    parsed = []
    for value in departures:
        try:
            td = str_to_time_delta(value)
        except (TypeError, ValueError):
            continue
        if timedelta(0) <= td < timedelta(days=1):
            parsed.append(td)

    parsed = sorted(set(parsed))
    if len(parsed) < 6:
        return False

    gaps = [
        int((current - previous).total_seconds() // 60)
        for previous, current in zip(parsed, parsed[1:])
    ]
    one_minute_gaps = sum(gap <= 1 for gap in gaps)
    return one_minute_gaps >= 4 and one_minute_gaps / len(gaps) >= 0.30

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

    if has_suspicious_departure_intervals(departures_base):
        return [], False

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



# --- FULL SCHEDULE MATRIX & EXPORT HELPERS ---
def build_full_matrix_dataframe(line_code, regime_name):
    stops_list = st.session_state["stops_c1"] if line_code == "C1" else st.session_state["stops_c2"]
    if line_code == "C1":
        if regime_name == "Dias Úteis":
            deps = st.session_state["dep_dias_c1"]
        elif regime_name == "Sábados":
            deps = st.session_state["dep_sab_c1"]
        else:
            deps = st.session_state["dep_dom_c1"]
    else:
        if regime_name == "Dias Úteis":
            deps = st.session_state["dep_dias_c2"]
        elif regime_name == "Sábados":
            deps = st.session_state["dep_sab_c2"]
        else:
            deps = st.session_state["dep_dom_c2"]

    matrix_rows = []
    for idx, (s_name, s_off, s_lat, s_lon) in enumerate(stops_list, 1):
        row = {
            "Ordem": idx,
            "Offset (min)": f"+{s_off} min",
            "Paragem de Autocarro": s_name
        }
        for d in deps:
            arr_td = str_to_time_delta(d) + timedelta(minutes=s_off)
            row[f"Partida {d}"] = format_timedelta(arr_td)
        matrix_rows.append(row)

    return pd.DataFrame(matrix_rows), deps

def generate_full_line_excel(line_code):
    stops_list = st.session_state["stops_c1"] if line_code == "C1" else st.session_state["stops_c2"]
    if line_code == "C1":
        dep_dias = st.session_state["dep_dias_c1"]
        dep_sab = st.session_state["dep_sab_c1"]
        dep_dom = st.session_state["dep_dom_c1"]
    else:
        dep_dias = st.session_state["dep_dias_c2"]
        dep_sab = st.session_state["dep_sab_c2"]
        dep_dom = st.session_state["dep_dom_c2"]

    wb = Workbook()
    wb.remove(wb.active)

    regimes_data = [
        ("Dias Úteis", dep_dias),
        ("Sábados", dep_sab),
        ("Domingos e Feriados", dep_dom)
    ]

    for regime_title, deps in regimes_data:
        ws = wb.create_sheet(title=regime_title)
        header = ["Ordem", "Offset (min)", "Paragem de Autocarro"] + [f"Partida {d}" for d in deps]
        ws.append(header)

        for idx, (s_name, s_off, s_lat, s_lon) in enumerate(stops_list, 1):
            row = [idx, f"+{s_off} min", s_name]
            for d in deps:
                arr_td = str_to_time_delta(d) + timedelta(minutes=s_off)
                row.append(format_timedelta(arr_td))
            ws.append(row)

        ws.freeze_panes = "D2"
        ws.row_dimensions[1].height = 26
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1B4F72")
            cell.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)

        for row in ws.iter_rows(min_row=2):
            for col_idx, cell in enumerate(row):
                if col_idx < 3:
                    cell.alignment = Alignment(vertical="center", horizontal="left" if col_idx == 2 else "center")
                    cell.font = Font(bold=(col_idx == 2))
                else:
                    cell.alignment = Alignment(vertical="center", horizontal="center")

        ws.column_dimensions["A"].width = 10
        ws.column_dimensions["B"].width = 14
        ws.column_dimensions["C"].width = 38
        for c in range(4, len(deps) + 4):
            ws.column_dimensions[get_column_letter(c)].width = 15

    # Add Stops Sheet
    ws_stops = wb.create_sheet(title="Paragens & Coordenadas")
    ws_stops.append(["Linha", "Ordem", "Offset (min)", "Nome da Paragem", "Ponto de Referência", "Latitude", "Longitude"])
    for idx, (s_name, s_off, s_lat, s_lon) in enumerate(stops_list, 1):
        ref = PONTOS_REFERENCIA.get(s_name, "-")
        ws_stops.append([line_code, idx, s_off, s_name, ref, s_lat, s_lon])

    ws_stops.freeze_panes = "D2"
    ws_stops.row_dimensions[1].height = 26
    for cell in ws_stops[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="245A73")
        cell.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)

    ws_stops.column_dimensions["A"].width = 10
    ws_stops.column_dimensions["B"].width = 10
    ws_stops.column_dimensions["C"].width = 14
    ws_stops.column_dimensions["D"].width = 38
    ws_stops.column_dimensions["E"].width = 45
    ws_stops.column_dimensions["F"].width = 16
    ws_stops.column_dimensions["G"].width = 16

    for ws in wb.worksheets:
        ws.auto_filter.ref = ws.dimensions

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.getvalue()

def generate_full_pdf_matrix_report(line_code, regime_label):
    stops_list = st.session_state["stops_c1"] if line_code == "C1" else st.session_state["stops_c2"]
    if line_code == "C1":
        if regime_label == "Dias Úteis":
            deps = st.session_state["dep_dias_c1"]
        elif regime_label == "Sábados":
            deps = st.session_state["dep_sab_c1"]
        else:
            deps = st.session_state["dep_dom_c1"]
    else:
        if regime_label == "Dias Úteis":
            deps = st.session_state["dep_dias_c2"]
        elif regime_label == "Sábados":
            deps = st.session_state["dep_sab_c2"]
        else:
            deps = st.session_state["dep_dom_c2"]

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"MUV Viseu - Horarios Completos Linha {line_code}", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"Regime: {regime_label} | Fonte Oficial MUV (Em vigor: {st.session_state.get('version_label', '1 de Março de 2026')})", align="C")
    pdf.ln(8)

    chunk_size = 9
    dep_chunks = [deps[i:i + chunk_size] for i in range(0, len(deps), chunk_size)]

    for chunk_idx, dep_chunk in enumerate(dep_chunks):
        if chunk_idx > 0:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 8, f"MUV Viseu - Horarios Linha {line_code} ({regime_label}) - Pagina {chunk_idx + 1}", align="C")
            pdf.ln(6)

        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(8, 7, "Ord", border=1, align="C")
        pdf.cell(14, 7, "Offset", border=1, align="C")
        pdf.cell(70, 7, "Paragem", border=1)

        for dep in dep_chunk:
            pdf.cell(19, 7, f"P {dep}", border=1, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 7.5)
        for s_idx, (s_name, s_off, s_lat, s_lon) in enumerate(stops_list, 1):
            pdf.cell(8, 5.5, str(s_idx), border=1, align="C")
            pdf.cell(14, 5.5, f"+{s_off}m", border=1, align="C")
            clean_name = s_name.encode("latin-1", "replace").decode("latin-1")
            pdf.cell(70, 5.5, clean_name[:38], border=1)
            for dep in dep_chunk:
                arr_td = str_to_time_delta(dep) + timedelta(minutes=s_off)
                pdf.cell(19, 5.5, format_timedelta(arr_td), border=1, align="C")
            pdf.ln()

    return bytes(pdf.output())


# --- USER INTERFACE ---
st.title("🚌 MUViseu Circulares (v20")
st.info(f"📅 **Versão dos Horários em Vigor:** {st.session_state.get('version_label', '1 de Março de 2026')} *(Fonte Oficial MUV)*")

st.markdown("Aplicação interativa em Python e Streamlit com **Comparador Inteligente C1 vs C2**, **Gestor de Favoritos**, **mapa interativo Folium**, **PDF upload com validação de parser**, e **exportação .ICS/PDF/CSV**.")

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
    all_stops = list(dict.fromkeys(stops_c1_names + stops_c2_names))
    available_stops = all_stops

# Handle Favorite selection trigger
if "sel_origem" not in st.session_state:
    st.session_state["sel_origem"] = available_stops[0]
if "sel_destino" not in st.session_state:
    st.session_state["sel_destino"] = available_stops[min(13, len(available_stops)-1)]

if st.session_state["sel_origem"] not in available_stops:
    st.session_state["sel_origem"] = available_stops[0]
if st.session_state["sel_destino"] not in available_stops:
    st.session_state["sel_destino"] = available_stops[min(13, len(available_stops)-1)]

origem = st.sidebar.selectbox("Paragem de Origem", available_stops, format_func=format_stop_label, key="sel_origem")
destino = st.sidebar.selectbox("Paragem de Destino", available_stops, format_func=format_stop_label, key="sel_destino")

if st.sidebar.button("⏱️ Usar Hora Atual"):
    st.session_state["time_input_val"] = datetime.now().time()

initial_time = st.session_state.get("time_input_val", time(8, 0))
horario_desejado = st.sidebar.time_input("Horário Desejado a partir de", value=initial_time)
n_horarios = st.sidebar.number_input("Número de próximos horários (N)", min_value=1, max_value=10, value=3, step=1)

# FAVORITES MANAGEMENT SECTION
st.sidebar.markdown("---")
st.sidebar.header("⭐ Percursos Favoritos")

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


# PDF -> EXCEL CONVERTER SECTION
st.sidebar.markdown("---")
st.sidebar.header("📄 Converter PDF oficial para Excel")
st.sidebar.caption("Extrai os horários dos quadros oficiais C1/C2 e prepara um Excel para revisão e importação.")
uploaded_pdf_converter = st.sidebar.file_uploader("Carregar PDF oficial C1/C2", type=["pdf"], key="official_pdf_converter")
if uploaded_pdf_converter is not None:
    try:
        excel_bytes, conversion_report = convert_official_pdf_to_excel(uploaded_pdf_converter)
        st.sidebar.success(f"PDF identificado: {conversion_report['line']} — {conversion_report['date']}")
        st.sidebar.write(f"Paragens: {conversion_report['stop_count']} | Dias úteis: {conversion_report['weekday_count']} | Sábados: {conversion_report['saturday_count']} | Domingos/feriados: {conversion_report['sunday_count']}")
        if conversion_report["audit_pending"]:
            st.sidebar.warning(f"Existem {conversion_report['audit_pending']} correspondências por validar. O Excel será gerado, mas a importação ficará bloqueada até corrigir a folha Conferência PDF e completar as coordenadas em falta.")
        else:
            st.sidebar.success("Todas as paragens foram correspondidas com a lista da aplicação.")
        st.sidebar.download_button(
            "⬇ Descarregar Excel convertido",
            data=excel_bytes,
            file_name=f"MUViseu_{conversion_report['line']}_{conversion_report['date']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_converted_excel"
        )
    except Exception as conversion_error:
        st.sidebar.error(f"Conversão bloqueada: {conversion_error}")

# EXCEL UPLOADER SECTION IN SIDEBAR
st.sidebar.markdown("---")
st.sidebar.header("📊 Atualizar Dados por Excel")
st.sidebar.caption("Importe um ficheiro no modelo MUViseu. O PDF deve ser convertido e validado antes desta etapa.")
uploaded_excel = st.sidebar.file_uploader("Carregar Excel de Horários", type=["xlsx"])

if uploaded_excel is not None:
    line_parsed, new_stops, new_departures, excel_date_obj, excel_errors = parse_excel_schedules(uploaded_excel)
    curr_date_str = st.session_state.get("version_date", DEFAULT_VERSION_DATE)
    try:
        cy, cm, cd = map(int, curr_date_str.split("-"))
        curr_date_obj = date(cy, cm, cd)
    except Exception:
        curr_date_obj = date(2026, 3, 1)

    is_older = excel_date_obj is not None and excel_date_obj < curr_date_obj
    is_same = excel_date_obj is not None and excel_date_obj == curr_date_obj
    excel_import_valid = not excel_errors and line_parsed in ("C1", "C2")

    with st.sidebar.expander("🔍 Pré-visualização e Validação do Excel", expanded=True):
        st.write(f"**Linha identificada:** {line_parsed or 'Inválida'}")
        st.write(f"**Data de entrada em vigor:** `{excel_date_obj or 'Em falta'}`")
        st.write(f"**Paragens validadas:** {len(new_stops)}")
        st.write("**Regimes de horários:** " + (", ".join(new_departures.keys()) if new_departures else "Nenhum"))
        if excel_errors:
            for err in excel_errors:
                st.error("⛔ " + err)
        elif is_older:
            st.error("⛔ Este ficheiro é anterior à versão atualmente ativa.")
        elif is_same:
            st.info("ℹ O ficheiro tem a mesma data da versão ativa.")
        else:
            st.success("✅ Estrutura e dados validados. Reveja antes de importar.")

    if not excel_import_valid or is_older:
        st.sidebar.warning("Importação bloqueada. Corrija os erros indicados ou utilize uma versão mais recente.")
    else:
        if st.sidebar.button("✅ Confirmar e Importar Excel"):
            line_key = line_parsed.lower()
            st.session_state[f"stops_{line_key}"] = new_stops
            for suffix, values in new_departures.items():
                st.session_state[f"{suffix}_{line_key}"] = values
            st.session_state["version_date"] = str(excel_date_obj)
            st.session_state["version_label"] = excel_date_obj.strftime("%d/%m/%Y")
            save_persisted_data()
            st.sidebar.success(f"Dados da linha {line_parsed} guardados.")
            st.rerun()


# Main Output Layout with Tabs
tab_consultar, tab_matriz, tab_mapa, tab_detalhes = st.tabs([
    "🔍 Consulta & Comparador", 
    "📊 Planilha Completa (C1/C2)", 
    "🗺️ Mapa do Percurso", 
    "📱 Resumo Compacto / Mobile"
])

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
        trips_c1, valid_c1 = calculate_next_trips("C1", tipo_dia, origem, destino, horario_desejado, n_horarios)
        trips_c2, valid_c2 = calculate_next_trips("C2", tipo_dia, origem, destino, horario_desejado, n_horarios)

        if not valid_c1 or not valid_c2:
            st.warning(
                "⚠️ Foram detetados dados de horários inválidos ou com intervalos anormalmente curtos. "
                "Os resultados afetados foram bloqueados para evitar apresentar partidas falsas. "
                "Verifique os horários guardados ou use «Restaurar Dados Oficiais Padrão» na barra lateral."
            )

        if modo_linha == "⚡ Comparar C1 e C2 (Mais Rápida)":
            st.markdown("### ⚡ Comparador Inteligente: C1 vs C2")

            if not trips_c1 and not trips_c2:
                st.info("ℹ️ Não foram encontradas viagens para nenhuma das linhas com as paragens selecionadas.")
            else:
                best_line = None
                time_saved = 0
                
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

                if best_line in ["C1", "C2"]:
                    rec_trip = trips_c1[0] if best_line == "C1" else trips_c2[0]
                    saved_msg = f" — chega {time_saved} minuto(s) mais cedo!" if time_saved > 0 else "!"
                    st.success(
                        f"🚀 **RECOMENDAÇÃO IDEAL:** Apanhe a **Linha {best_line}** com partida às **{rec_trip['Partida da Origem']}** "
                        f"e chegada às **{rec_trip['Chegada ao Destino']}**{saved_msg}"
                    )
                elif best_line == "Empate":
                    st.info("🤝 **EMPATE:** Ambas as linhas C1 e C2 chegam ao destino exatamente no mesmo horário!")

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


with tab_matriz:
    st.subheader("📊 Planilha Completa & Matriz de Horários")
    st.markdown("Consulte e exporte a **grelha integral de partidas do terminal**, a **matriz de horários calculados para todas as paragens** e a **lista de coordenadas oficiais** para as **Linhas C1 e C2**.")

    col_mat_l, col_mat_r = st.columns([1, 1])
    with col_mat_l:
        mat_line = st.selectbox(
            "Linha a Consultar / Exportar",
            ["Linha C1", "Linha C2"],
            index=0 if modo_linha != "Linha C2" else 1,
            key="sel_mat_line"
        )
    with col_mat_r:
        mat_regime = st.selectbox(
            "Regime de Funcionamento",
            ["Dias Úteis", "Sábados", "Domingos e Feriados"],
            index=0 if tipo_dia == "Dias Úteis" else (1 if tipo_dia == "Sábados" else 2),
            key="sel_mat_regime"
        )

    target_line_code = "C1" if mat_line == "Linha C1" else "C2"

    df_matrix, mat_deps = build_full_matrix_dataframe(target_line_code, mat_regime)
    stops_active = st.session_state["stops_c1"] if target_line_code == "C1" else st.session_state["stops_c2"]

    st.markdown(f"### 📋 Matriz de Horários — {mat_line} ({mat_regime})")
    st.caption(f"Exibindo **{len(stops_active)} paragens** e **{len(mat_deps)} partidas** do terminal. Deslize a tabela horizontalmente para ver todos os horários do dia.")
    
    st.dataframe(df_matrix, use_container_width=True, height=440)

    # Summary metrics for full matrix
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("🚌 Total de Partidas Terminal", f"{len(mat_deps)} viagens")
    with col_m2:
        st.metric("🌅 Primeira Partida", mat_deps[0] if mat_deps else "-")
    with col_m3:
        st.metric("🌙 Última Partida", mat_deps[-1] if mat_deps else "-")
    with col_m4:
        st.metric("🛑 Total de Paragens no Circuito", f"{len(stops_active)} paragens")

    st.markdown("---")
    st.markdown(f"### 📥 Exportação da Planilha Completa — {mat_line}")
    st.markdown("Descarregue a grelha integral com todos os horários e paragens no formato à sua escolha:")

    exp_m1, exp_m2, exp_m3 = st.columns(3)

    with exp_m1:
        try:
            excel_bytes = generate_full_line_excel(target_line_code)
            st.download_button(
                label=f"📊 Descarregar Planilha Excel Completa (.XLSX)",
                data=excel_bytes,
                file_name=f"matriz_completa_horarios_{target_line_code}_MUV.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Inclui folhas separadas para Dias Úteis, Sábados, Domingos/Feriados e Coordenadas."
            )
        except Exception as exc:
            st.error(f"Erro ao gerar Excel: {exc}")

    with exp_m2:
        csv_bytes = df_matrix.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"📄 Descarregar Matriz CSV ({mat_regime})",
            data=csv_bytes,
            file_name=f"matriz_horarios_{target_line_code}_{mat_regime.replace(' ', '_')}.csv",
            mime="text/csv",
            help="Descarrega a matriz de horários do regime selecionado em formato CSV."
        )

    with exp_m3:
        try:
            pdf_bytes = generate_full_pdf_matrix_report(target_line_code, mat_regime)
            st.download_button(
                label=f"📕 Descarregar Relatório PDF Completo",
                data=pdf_bytes,
                file_name=f"relatorio_matriz_completa_{target_line_code}_{mat_regime.replace(' ', '_')}.pdf",
                mime="application/pdf",
                help="Gera relatório em PDF horizontal com a grelha completa de horários."
            )
        except Exception as exc:
            st.error(f"Erro ao gerar PDF: {exc}")

    with st.expander(f"📍 Ver Lista Completa de Paragens e Coordenadas ({mat_line})", expanded=False):
        stops_table_data = []
        for idx, (s_name, s_off, s_lat, s_lon) in enumerate(stops_active, 1):
            stops_table_data.append({
                "Ordem": idx,
                "Offset": f"+{s_off} min",
                "Nome da Paragem": s_name,
                "Ponto de Referência": PONTOS_REFERENCIA.get(s_name, "-"),
                "Latitude": s_lat,
                "Longitude": s_lon
            })
        st.dataframe(pd.DataFrame(stops_table_data), use_container_width=True)



with tab_mapa:
    st.subheader("🗺️ Mapa do Percurso Urbano")
    
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

    m = folium.Map(
        location=[40.6600, -7.9120], 
        zoom_start=14, 
        tiles=tile_url, 
        attr=tile_attr
    )

    fit_points = [[s[2], s[3]] for s in map_stops]
    if orig_raw_coords: fit_points.append([orig_raw_coords[0], orig_raw_coords[1]])
    if dest_raw_coords: fit_points.append([dest_raw_coords[0], dest_raw_coords[1]])

    lats = [p[0] for p in fit_points]
    lons = [p[1] for p in fit_points]
    if lats and lons:
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=(25, 25))
    
    full_path_coords = [[s[2], s[3]] for s in map_stops]
    folium.PolyLine(
        full_path_coords,
        color="#0066FF",
        weight=4,
        opacity=0.75,
        tooltip=f"Circuito Completo da Linha {target_map_line}"
    ).add_to(m)

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
st.caption("MUViseu Circulares v20 - Sistema Inteligente de Horários & Mobilidade Urbana de Viseu.")