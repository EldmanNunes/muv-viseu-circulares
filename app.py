import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import pydeck as pdk
from fpdf import FPDF
import io
import json
import os
import re
import pdfplumber

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MUViseu Circulares - Horários Linhas C1 e C2",
    page_icon="🚌",
    layout="wide"
)

# --- CACHE / PERSISTENCE FILE ---
CACHE_FILE = "custom_schedules.json"

# --- DEFAULT DATA ---
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
    ("Quinta do Galo 2", 4, 40.6530, -7.9120),
    ("Quinta de Jugueiros", 5, 40.6515, -7.9135),
    ("Residências IPV", 6, 40.6495, -7.9150),
    ("Rua Nova", 7, 40.6480, -7.9160),
    ("Cidade Politécnica-IPV", 8, 40.6465, -7.9170),
    ("Reg Infantaria-IPV 1", 9, 40.6485, -7.9180),
    ("Reg Infantaria-IPV 2", 10, 40.6500, -7.9185),
    ("Paulo VI-25 Abril", 11, 40.6520, -7.9150),
    ("25 Abril-Liceu 2", 12, 40.6540, -7.9130),
    ("Rossio 2", 13, 40.6568, -7.9128),
    ("Alberto Sampaio 1", 14, 40.6580, -7.9110),
    ("Alberto Sampaio 2", 15, 40.6590, -7.9095),
    ("N. S. Fátima-Igreja", 16, 40.6605, -7.9080),
    ("J Maria Escrivá-Hotel 2", 17, 40.6620, -7.9070),
    ("José Maria Escrivá 2", 18, 40.6635, -7.9060),
    ("Monte Belo-J Infância 1", 19, 40.6650, -7.9050),
    ("Monte Belo-Estádio 1", 20, 40.6665, -7.9040),
    ("Campo dos Trambelos", 21, 40.6680, -7.9030),
    ("Balsa 1", 22, 40.6690, -7.9020),
    ("César Anjo 1", 23, 40.6700, -7.9010),
    ("Bombeiros Voluntários", 24, 40.6685, -7.9080),
    ("COMV 1", 25, 40.6670, -7.9120),
    ("Fonte Cibernética 2", 26, 40.6660, -7.9150),
    ("Av Europa-Tribunal 2", 27, 40.6650, -7.9180),
    ("M Ferreira Figueiredo 1", 30, 40.6680, -7.9220),
    ("Pedro Henriques 1", 31, 40.6700, -7.9240),
    ("Escola Viriato 2", 33, 40.6720, -7.9260),
    ("Estrada Velha Abraveses", 35, 40.6740, -7.9280),
    ("Cava de Viriato 2", 37, 40.6650, -7.9130),
    ("Feira de S. Mateus 2", 38, 40.6620, -7.9135),
    ("Porta dos Cavaleiros 1", 39, 40.6595, -7.9125),
    ("Mouzinho de Albuquerque", 40, 40.6580, -7.9140),
    ("Capitão Silva Pereira", 41, 40.6570, -7.9155),
    ("Cap S Pereira-S Cristina", 42, 40.6560, -7.9165),
    ("5 de Outubro 1", 43, 40.6550, -7.9150),
    ("Rua Seminário", 44, 40.6540, -7.9135),
    ("Dr Azeredo Perdigão 1", 45, 40.6550, -7.9120),
    ("General Humberto Delgado", 46, 40.6560, -7.9125),
    ("Rossio 1", 48, 40.6568, -7.9128),
    ("25 Abril-Liceu 1", 50, 40.6540, -7.9130),
    ("Nuno Alvares Pereira", 51, 40.6525, -7.9140),
    ("Escola João de Barros 1", 52, 40.6510, -7.9130),
    ("Manuel Silva Almeida 1", 53, 40.6500, -7.9120),
    ("Paulo VI-25 Abril (Regresso)", 54, 40.6520, -7.9150),
    ("Escola Grão Vasco", 55, 40.6535, -7.9110),
    ("Alexandre Lucena e Vale", 56, 40.6550, -7.9090),
    ("10 de Junho-Cemitério 1", 57, 40.6565, -7.9075),
    ("Rei D Duarte-Mesuras", 58, 40.6575, -7.9070),
    ("Hospital S Teotónio", 58, 40.6580, -7.9068),
    ("Interface Hospital (Chegada)", 60, 40.6582, -7.9065)
]

DEFAULT_STOPS_C2 = [
    ("Interface Hospital", 0, 40.6582, -7.9065),
    ("Biblioteca-Loja Cidadão", 1, 40.6570, -7.9080),
    ("10 de Junho-Cemitério 2", 2, 40.6565, -7.9075),
    ("Rua Mendonça", 3, 40.6550, -7.9090),
    ("Escola Grão Vasco", 3, 40.6535, -7.9110),
    ("Praça de Goa", 4, 40.6520, -7.9120),
    ("Estevão Lopes Morago 1", 5, 40.6510, -7.9125),
    ("Manuel Silva Almeida 2", 6, 40.6500, -7.9120),
    ("Escola João de Barros 2", 7, 40.6510, -7.9130),
    ("António Esteves Correia", 8, 40.6525, -7.9135),
    ("25 Abril-Liceu 2", 9, 40.6540, -7.9130),
    ("Rossio 2", 10, 40.6568, -7.9128),
    ("Alves Martins", 11, 40.6575, -7.9135),
    ("Dr Azeredo Perdigão 2", 12, 40.6550, -7.9120),
    ("Monsenhor Celso T Silva", 13, 40.6545, -7.9140),
    ("Universidade Católica", 14, 40.6535, -7.9160),
    ("5 de Outubro 2", 15, 40.6550, -7.9150),
    ("S Cristina-Cap S Pereira", 16, 40.6560, -7.9165),
    ("Cap S Pereira-Fontelo", 17, 40.6575, -7.9150),
    ("Largo Santo António", 18, 40.6585, -7.9135),
    ("Porta dos Cavaleiros 2", 19, 40.6595, -7.9125),
    ("Feira de S Mateus 1", 20, 40.6620, -7.9135),
    ("Cava de Viriato 1", 21, 40.6650, -7.9130),
    ("Av Bélgica-Alf Miguel 1", 22, 40.6670, -7.9180),
    ("Avenida Bélgica 2", 23, 40.6685, -7.9200),
    ("Pedro Henriques 1", 24, 40.6700, -7.9240),
    ("Pedro Henriques 2", 25, 40.6710, -7.9250),
    ("M Ferreira Figueiredo 2", 27, 40.6680, -7.9220),
    ("Avenida Europa", 29, 40.6660, -7.9200),
    ("Av Europa-Tribunal 1", 31, 40.6650, -7.9180),
    ("Fonte Cibernética 1", 32, 40.6660, -7.9150),
    ("COMV 2", 33, 40.6670, -7.9120),
    ("César Anjo 2", 34, 40.6700, -7.9010),
    ("Balsa 2", 35, 40.6690, -7.9020),
    ("Cidade Aveiro", 36, 40.6675, -7.9030),
    ("Monte Belo-Estádio 2", 37, 40.6665, -7.9040),
    ("Monte Belo-J Infância 2", 38, 40.6650, -7.9050),
    ("José Maria Escrivá 1", 39, 40.6635, -7.9060),
    ("J Maria Escrivá-Hotel 1", 40, 40.6620, -7.9070),
    ("Engrácia Carrilho-Igreja", 41, 40.6600, -7.9085),
    ("Colégio Imac Conceição", 42, 40.6590, -7.9100),
    ("Alberto Sampaio 3", 43, 40.6580, -7.9110),
    ("Rossio 1", 44, 40.6568, -7.9128),
    ("25 Abril-Liceu 1", 45, 40.6540, -7.9130),
    ("25 Abril-Paulo VI", 45, 40.6520, -7.9150),
    ("Reg Infantaria", 46, 40.6500, -7.9185),
    ("Reg Infantaria-IPV 3", 47, 40.6485, -7.9180),
    ("C Politécnica-Escola", 48, 40.6465, -7.9170),
    ("Madre Rita de Jesus 1", 49, 40.6480, -7.9155),
    ("M Rita Jesus-Escola 1", 50, 40.6495, -7.9140),
    ("M Rita Jesus-C Saúde", 51, 40.6510, -7.9125),
    ("M R Jesus-Int V Fontes", 52, 40.6525, -7.9110),
    ("Quinta do Galo 1", 53, 40.6530, -7.9120),
    ("Quinta da Alagoa", 54, 40.6545, -7.9100),
    ("Escola Aquilino Ribeiro", 55, 40.6560, -7.9085),
    ("Rei D Duarte-Hospital 2", 56, 40.6575, -7.9080),
    ("Hospital S Teotónio", 57, 40.6580, -7.9068),
    ("Interface Hospital (Chegada)", 60, 40.6582, -7.9065)
]

# --- LANDMARKS DICTIONARY ---
PONTOS_REFERENCIA = {
    "Interface Hospital": "🏥 Hospital de São Teotónio / Interface Transportes",
    "Rei D Duarte-Hospital 1": "🏥 Próximo ao Hospital S. Teotónio",
    "Quinta D´el Rei": "🏡 Quinta D'el Rei",
    "Dr A Alves-C Comercial 1": "🛒 Supermercado Continente / Zona Comercial",
    "Quinta do Galo 2": "🏢 Quinta do Galo",
    "Quinta do Galo 1": "🏢 Quinta do Galo",
    "Quinta de Jugueiros": "🏫 Jugueiros",
    "Residências IPV": "🎓 Residências Universitárias IPV",
    "Rua Nova": "📍 Rua Nova",
    "Cidade Politécnica-IPV": "🎓 IPV - Instituto Politécnico de Viseu (Campus)",
    "C Politécnica-Escola": "🎓 IPV - Instituto Politécnico de Viseu",
    "Reg Infantaria-IPV 1": "🎖️ Regimento de Infantaria n.º 14 / IPV",
    "Reg Infantaria-IPV 2": "🎖️ Regimento de Infantaria n.º 14",
    "Reg Infantaria-IPV 3": "🎖️ Regimento de Infantaria n.º 14",
    "Reg Infantaria": "🎖️ Regimento de Infantaria n.º 14",
    "Paulo VI-25 Abril": "⛪ Colégio Via Sacra / Av. Paulo VI",
    "25 Abril-Liceu 2": "🏫 Escola Secundária Alves Martins (Liceu)",
    "25 Abril-Liceu 1": "🏫 Escola Secundária Alves Martins (Liceu)",
    "25 Abril-Paulo VI": "⛪ Av. Paulo VI",
    "Rossio 2": "🌳 Praça da República (Rossio) / Centro Histórico",
    "Rossio 1": "🌳 Praça da República (Rossio) / Centro Histórico",
    "Alberto Sampaio 1": "🏛️ Av. Alberto Sampaio",
    "Alberto Sampaio 2": "🏛️ Av. Alberto Sampaio",
    "Alberto Sampaio 3": "🏛️ Av. Alberto Sampaio",
    "N. S. Fátima-Igreja": "⛪ Igreja de Nossa Senhora de Fátima",
    "J Maria Escrivá-Hotel 2": "🏨 Zona Hoteleira / Av. José Maria Escrivá",
    "J Maria Escrivá-Hotel 1": "🏨 Zona Hoteleira / Av. José Maria Escrivá",
    "José Maria Escrivá 2": "📍 Av. José Maria Escrivá",
    "José Maria Escrivá 1": "📍 Av. José Maria Escrivá",
    "Monte Belo-J Infância 1": "🏫 Monte Belo / Jardim de Infância",
    "Monte Belo-J Infância 2": "🏫 Monte Belo / Jardim de Infância",
    "Monte Belo-Estádio 1": "⚽ Monte Belo / Estádio do Fontelo",
    "Monte Belo-Estádio 2": "⚽ Monte Belo / Estádio do Fontelo",
    "Campo dos Trambelos": "🏟️ Campo dos Trambelos",
    "Balsa 1": "📍 Balsa",
    "Balsa 2": "📍 Balsa",
    "César Anjo 1": "📍 Rua César Anjo",
    "César Anjo 2": "📍 Rua César Anjo",
    "Bombeiros Voluntários": "🚒 Quartel dos Bombeiros Voluntários",
    "COMV 1": "🚌 Central de Camionagem / Rodoviária (COMV)",
    "COMV 2": "🚌 Central de Camionagem / Rodoviária (COMV)",
    "Fonte Cibernética 2": "⛲ Fonte Cibernética / Parque Aquilino Ribeiro",
    "Fonte Cibernética 1": "⛲ Fonte Cibernética / Parque Aquilino Ribeiro",
    "Av Europa-Tribunal 2": "⚖️ Tribunal de Viseu / Av. da Europa",
    "Av Europa-Tribunal 1": "⚖️ Tribunal de Viseu / Av. da Europa",
    "M Ferreira Figueiredo 1": "📍 Av. Manuel Ferreira Figueiredo",
    "M Ferreira Figueiredo 2": "📍 Av. Manuel Ferreira Figueiredo",
    "Pedro Henriques 1": "📍 D. Pedro Henriques",
    "Pedro Henriques 2": "📍 D. Pedro Henriques",
    "Escola Viriato 2": "🏫 Escola Secundária Viriato",
    "Estrada Velha Abraveses": "🛣️ Abraveses (Estrada Velha)",
    "Cava de Viriato 2": "🛡️ Cava de Viriato / Monumento",
    "Cava de Viriato 1": "🛡️ Cava de Viriato / Monumento",
    "Feira de S. Mateus 2": "🎡 Campo de Viriato / Feira de São Mateus",
    "Feira de S Mateus 1": "🎡 Campo de Viriato / Feira de São Mateus",
    "Porta dos Cavaleiros 1": "🏛️ Porta dos Cavaleiros / Centro Histórico",
    "Porta dos Cavaleiros 2": "🏛️ Porta dos Cavaleiros / Centro Histórico",
    "Mouzinho de Albuquerque": "📍 Mouzinho de Albuquerque",
    "Capitão Silva Pereira": "📍 Capitão Silva Pereira",
    "Cap S Pereira-S Cristina": "⛪ Capela de Santa Cristina",
    "S Cristina-Cap S Pereira": "⛪ Capela de Santa Cristina",
    "Cap S Pereira-Fontelo": "🌲 Parque do Fontelo",
    "5 de Outubro 1": "🛍️ Rua 5 de Outubro",
    "5 de Outubro 2": "🛍️ Rua 5 de Outubro",
    "Rua Seminário": "⛪ Seminário Maior de Viseu",
    "Dr Azeredo Perdigão 1": "🛍️ Shopping Palácio do Gelo (Acesso Norte)",
    "Dr Azeredo Perdigão 2": "🛍️ Shopping Palácio do Gelo (Acesso Norte)",
    "General Humberto Delgado": "📍 Av. General Humberto Delgado",
    "Nuno Alvares Pereira": "📍 Rua Nuno Álvares Pereira",
    "Escola João de Barros 1": "🏫 Escola Básica João de Barros",
    "Escola João de Barros 2": "🏫 Escola Básica João de Barros",
    "Manuel Silva Almeida 1": "🏡 Minha Casa - Manuel Silva Almeida",
    "Manuel Silva Almeida 2": "🏡 Minha Casa - Manuel Silva Almeida",
    "Paulo VI-25 Abril (Regresso)": "⛪ Av. Paulo VI",
    "Escola Grão Vasco": "🏫 Escola Secundária Grão Vasco",
    "Alexandre Lucena e Vale": "📍 Alexandre Lucena e Vale",
    "10 de Junho-Cemitério 1": "🪦 Cemitério de Viseu / Av. 10 de Junho",
    "10 de Junho-Cemitério 2": "🪦 Cemitério de Viseu / Av. 10 de Junho",
    "Rei D Duarte-Mesuras": "📍 Rei D. Duarte / Mesuras",
    "Rei D Duarte-Hospital 2": "🏥 Próximo ao Hospital S. Teotónio",
    "Hospital S Teotónio": "🏥 Hospital de São Teotónio",
    "Interface Hospital (Chegada)": "🏥 Hospital de São Teotónio (Chegada)",
    "Biblioteca-Loja Cidadão": "🏛️ Loja do Cidadão & Biblioteca Municipal",
    "Rua Mendonça": "📍 Rua Mendonça",
    "Praça de Goa": "📍 Praça de Goa",
    "Estevão Lopes Morago 1": "📍 Estêvão Lopes Morago",
    "António Esteves Correia": "📍 António Esteves Correia",
    "Alves Martins": "🏫 Escola Alves Martins",
    "Monsenhor Celso T Silva": "⛪ Monsenhor Celso T. Silva",
    "Universidade Católica": "🎓 Universidade Católica Portuguesa",
    "Largo Santo António": "⛪ Largo de Santo António",
    "Av Bélgica-Alf Miguel 1": "📍 Av. da Bélgica",
    "Avenida Bélgica 2": "📍 Av. da Bélgica",
    "Avenida Europa": "⚖️ Av. da Europa",
    "Cidade Aveiro": "📍 Cidade de Aveiro",
    "Engrácia Carrilho-Igreja": "⛪ Engrácia Carrilho",
    "Colégio Imac Conceição": "🏫 Colégio Imaculada Conceição",
    "Madre Rita de Jesus 1": "🏫 Madre Rita de Jesus",
    "M Rita Jesus-Escola 1": "🏫 Madre Rita de Jesus",
    "M Rita Jesus-C Saúde": "🏥 Centro de Saúde",
    "M R Jesus-Int V Fontes": "📍 Madre Rita de Jesus",
    "Quinta da Alagoa": "🛍️ Shopping Palácio do Gelo (Acesso Sul / Alagoa)",
    "Escola Aquilino Ribeiro": "🏫 Escola Básica Aquilino Ribeiro",
}

def get_stop_display_name(stop_name):
    ref = PONTOS_REFERENCIA.get(stop_name, "")
    if ref:
        return f"{stop_name} — {ref}"
    return stop_name

# --- PERSISTENCE HELPERS ---
def load_persisted_data():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception:
            pass
    return None

def save_persisted_data():
    data = {
        "stops_c1": st.session_state.get("stops_c1", DEFAULT_STOPS_C1),
        "stops_c2": st.session_state.get("stops_c2", DEFAULT_STOPS_C2),
        "dep_dias_c1": st.session_state.get("dep_dias_c1", DEFAULT_DEPARTURES_DIAS_UTEIS),
        "dep_sab_c1": st.session_state.get("dep_sab_c1", DEFAULT_DEPARTURES_SABADOS),
        "dep_dom_c1": st.session_state.get("dep_dom_c1", DEFAULT_DEPARTURES_DOMINGOS),
        "dep_dias_c2": st.session_state.get("dep_dias_c2", DEFAULT_DEPARTURES_DIAS_UTEIS),
        "dep_sab_c2": st.session_state.get("dep_sab_c2", DEFAULT_DEPARTURES_SABADOS),
        "dep_dom_c2": st.session_state.get("dep_dom_c2", DEFAULT_DEPARTURES_DOMINGOS),
        "favorites": st.session_state.get("favorites", [])
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

# --- PARSER FUNCTION FOR PDF UPLOAD ENHANCED ---
def parse_pdf_schedules(pdf_file):
    """
    Parses an uploaded MUV PDF file using pdfplumber to extract line, stop names,
    and departures separated for the 3 regimes: Dias Úteis, Sábados, Domingos e Feriados.
    """
    parsed_line = None
    parsed_stops = []
    
    deps_dias = []
    deps_sab = []
    deps_dom = []

    with pdfplumber.open(pdf_file) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text() or ""
            full_text += text + "\n"
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    clean_row = [c.strip() for c in row if c and c.strip()]
                    if len(clean_row) >= 2:
                        stop_candidate = clean_row[0]
                        if ":" in clean_row[1] and len(clean_row[1]) == 5:
                            if stop_candidate not in [s[0] for s in parsed_stops]:
                                offset = len(parsed_stops) * 2
                                parsed_stops.append((stop_candidate, offset, 40.6568, -7.9128))

        if "C1" in full_text or "Linha C1" in full_text:
            parsed_line = "C1"
        elif "C2" in full_text or "Linha C2" in full_text:
            parsed_line = "C2"

        # Split text by regime headers if present
        text_dias = ""
        text_fim = ""
        
        if "DIAS ÚTEIS" in full_text.upper():
            parts = re.split(r'DIAS\s+ÚTEIS', full_text, flags=re.IGNORECASE)
            if len(parts) > 1:
                subparts = re.split(r'SÁBADOS', parts[1], flags=re.IGNORECASE)
                text_dias = subparts[0]
                if len(subparts) > 1:
                    text_fim = subparts[1]
        
        if not text_dias:
            text_dias = full_text

        times_dias = re.findall(r'\b(?:[01]\d|2[0-3]):[0-5]\d\b', text_dias)
        if times_dias:
            deps_dias = sorted(list(set(times_dias)))

        if text_fim:
            times_fim = re.findall(r'\b(?:[01]\d|2[0-3]):[0-5]\d\b', text_fim)
            if times_fim:
                deps_sab = sorted(list(set(times_fim)))
        else:
            deps_sab = deps_dias

        # Filter times <= 12:00 for Domingos e Feriados (subgroup marked with **)
        times_dom = []
        for t in deps_sab:
            h = int(t.split(":")[0])
            if h <= 12:
                times_dom.append(t)
        deps_dom = sorted(list(set(times_dom))) if times_dom else deps_sab[:6]

    return {
        "line": parsed_line,
        "stops": parsed_stops,
        "deps_dias": deps_dias,
        "deps_sab": deps_sab,
        "deps_dom": deps_dom
    }

# --- HELPER FUNCTIONS ---
def str_to_time_delta(time_str: str) -> timedelta:
    h, m = map(int, time_str.split(":"))
    return timedelta(hours=h, minutes=m)

def format_timedelta(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    hours = (total_seconds // 3600) % 24
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

    if dest_offset > orig_offset:
        duration_min = dest_offset - orig_offset
        via_terminal = False
    else:
        duration_min = (60 - orig_offset) + dest_offset
        via_terminal = True

    ref_td = timedelta(hours=ref_time_obj.hour, minutes=ref_time_obj.minute)

    results = []
    for dep_str in departures_base:
        base_td = str_to_time_delta(dep_str)
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
    today = datetime.now().strftime("%Y%m%d")
    h_orig, m_orig = trip_time_str.split(":")
    h_dest, m_dest = dest_time_str.split(":")
    
    dtstart = f"{today}T{h_orig}{m_orig}00"
    dtend = f"{today}T{h_dest}{m_dest}00"
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//MUV Viseu//Horarios Bus//PT
BEGIN:VEVENT
SUMMARY:Autocarro MUV {line_code}: {orig_stop} -> {dest_stop}
DESCRIPTION:Viagem de autocarro MUV Viseu da {line_code}.\\nPartida: {trip_time_str}\\nChegada: {dest_time_str}
LOCATION:{orig_stop}, Viseu
DTSTART:{dtstart}
DTEND:{dtend}
END:VEVENT
END:VCALENDAR"""
    return ics_content.encode("utf-8")

# --- USER INTERFACE ---
st.title("🚌 Consultor MUViseu Circulares")
st.markdown("Aplicação interativa para consulta das **Linhas C1 e C2 do MUV Viseu**, com suporte a **3 Regimes (Dias Úteis, Sábados, Domingos/Feriados com **)**, **Pontos de Referência**, **Comparador C1 vs C2**, **Upload Inteligente de PDF**, **Favoritos** e **Exportação**.")

# Sidebar Settings
st.sidebar.header("⚙️ Parâmetros da Viagem")

modo_linha = st.sidebar.radio(
    "Escolha a Linha",
    ["⚡ Comparar C1 e C2 (Mais Rápida)", "Linha C1", "Linha C2"]
)

tipo_dia = st.sidebar.radio(
    "Regime do Dia", 
    ["Dias Úteis", "Sábados", "Domingos e Feriados (**)"]
)

stops_c1_names = [s[0] for s in st.session_state["stops_c1"]]
stops_c2_names = [s[0] for s in st.session_state["stops_c2"]]

if modo_linha == "Linha C1":
    raw_stops = stops_c1_names
elif modo_linha == "Linha C2":
    raw_stops = stops_c2_names
else:
    raw_stops = list(dict.fromkeys(stops_c1_names + stops_c2_names))

stop_display_map = {s: get_stop_display_name(s) for s in raw_stops}
display_options = [stop_display_map[s] for s in raw_stops]
reverse_map = {v: k for k, v in stop_display_map.items()}

if "sel_origem_raw" not in st.session_state:
    st.session_state["sel_origem_raw"] = raw_stops[0]
if "sel_destino_raw" not in st.session_state:
    st.session_state["sel_destino_raw"] = raw_stops[min(13, len(raw_stops)-1)]

if st.session_state["sel_origem_raw"] not in raw_stops:
    st.session_state["sel_origem_raw"] = raw_stops[0]
if st.session_state["sel_destino_raw"] not in raw_stops:
    st.session_state["sel_destino_raw"] = raw_stops[min(13, len(raw_stops)-1)]

cur_origem_display = stop_display_map[st.session_state["sel_origem_raw"]]
cur_destino_display = stop_display_map[st.session_state["sel_destino_raw"]]

sel_origem_disp = st.sidebar.selectbox("Paragem de Origem (pesquise por Rua ou Ponto de Interesse)", display_options, index=display_options.index(cur_origem_display))
sel_destino_disp = st.sidebar.selectbox("Paragem de Destino (pesquise por Rua ou Ponto de Interesse)", display_options, index=display_options.index(cur_destino_display))

origem = reverse_map[sel_origem_disp]
destino = reverse_map[sel_destino_disp]
st.session_state["sel_origem_raw"] = origem
st.session_state["sel_destino_raw"] = destino

if st.sidebar.button("⏱️ Usar Hora Atual"):
    st.session_state["time_input_val"] = datetime.now().time()

initial_time = st.session_state.get("time_input_val", time(8, 0))
horario_desejado = st.sidebar.time_input("Horário Desejado a partir de", value=initial_time)
n_horarios = st.sidebar.number_input("Número de próximos horários (N)", min_value=1, max_value=10, value=3, step=1)

# FAVORITES MANAGEMENT SECTION
st.sidebar.markdown("---")
st.sidebar.header("⭐ Percursos Favoritos")

def apply_favorite(fav_item):
    st.session_state["sel_origem_raw"] = fav_item["origem"]
    st.session_state["sel_destino_raw"] = fav_item["destino"]

fav_label = f"{origem} ➔ {destino}"
if st.sidebar.button("⭐ Guardar este Percurso nos Favoritos"):
    new_fav = {"origem": origem, "destino": destino, "modo": modo_linha}
    if new_fav not in st.session_state["favorites"]:
        st.session_state["favorites"].append(new_fav)
        save_persisted_data()
        st.sidebar.success(f"Guardado: {fav_label}")

if st.session_state["favorites"]:
    st.sidebar.caption("Clique num favorito para carregar instantaneamente:")
    for idx, fav in enumerate(st.session_state["favorites"]):
        col_f1, col_f2 = st.sidebar.columns([4, 1])
        with col_f1:
            st.button(f"📌 {fav['origem']} ➔ {fav['destino']}", key=f"fav_btn_{idx}", on_click=apply_favorite, args=(fav,))
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
    parsed_res = parse_pdf_schedules(uploaded_pdf)
    line_parsed = parsed_res["line"]
    new_stops = parsed_res["stops"]
    deps_dias = parsed_res["deps_dias"]
    deps_sab = parsed_res["deps_sab"]
    deps_dom = parsed_res["deps_dom"]
    
    target_line = line_parsed if line_parsed else ("C1" if modo_linha != "Linha C2" else "C2")
    
    with st.sidebar.expander("🔍 Pré-visualização dos 3 Regimes Detetados", expanded=True):
        st.write(f"**Linha Identificada:** {target_line}")
        st.write(f"**Paragens Detetadas:** {len(new_stops)}")
        st.markdown(f"• **💼 Dias Úteis:** {len(deps_dias)} horários")
        st.markdown(f"• **📅 Sábados:** {len(deps_sab)} horários")
        st.markdown(f"• **🔴 Domingos e Feriados (**):** {len(deps_dom)} horários")
        if deps_dias:
            st.caption(f"Amostra Dias Úteis: {', '.join(deps_dias[:4])}...")
        if deps_dom:
            st.caption(f"Amostra Domingos/Feriados (**): {', '.join(deps_dom[:4])}...")

    regime_target = st.sidebar.selectbox(
        "Aplicar atualização no regime:",
        ["Todos os 3 Regimes (Automático)", "Dias Úteis apenas", "Sábados apenas", "Domingos e Feriados (**) apenas"]
    )

    if st.sidebar.button("✅ Confirmar e Importar PDF"):
        suffix = target_line.lower()
        if new_stops:
            st.session_state[f"stops_{suffix}"] = new_stops

        if regime_target == "Todos os 3 Regimes (Automático)":
            if deps_dias: st.session_state[f"dep_dias_{suffix}"] = deps_dias
            if deps_sab: st.session_state[f"dep_sab_{suffix}"] = deps_sab
            if deps_dom: st.session_state[f"dep_dom_{suffix}"] = deps_dom
        elif regime_target == "Dias Úteis apenas" and deps_dias:
            st.session_state[f"dep_dias_{suffix}"] = deps_dias
        elif regime_target == "Sábados apenas" and deps_sab:
            st.session_state[f"dep_sab_{suffix}"] = deps_sab
        elif regime_target == "Domingos e Feriados (**) apenas" and deps_dom:
            st.session_state[f"dep_dom_{suffix}"] = deps_dom

        save_persisted_data()
        st.sidebar.success(f"✅ Dados dos 3 regimes atualizados e guardados para a Linha {target_line}!")

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
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    st.sidebar.info("Dados restaurados para a versão oficial MUV Set/2025.")

# Main Output Layout with Tabs
tab_consultar, tab_mapa, tab_detalhes = st.tabs([
    "🔍 Consulta & Comparador", 
    "🗺️ Mapa do Percurso", 
    "📱 Resumo Compacto / Mobile"
])

with tab_consultar:
    st.subheader(f"📍 Percurso: {origem} ➔ {destino}")
    
    orig_ref = PONTOS_REFERENCIA.get(origem, "")
    dest_ref = PONTOS_REFERENCIA.get(destino, "")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.info(f"🟢 **Origem:** {origem}\n\n*Ponto de Referência:* {orig_ref if orig_ref else 'Paragem Urbana'}")
    with col_r2:
        st.info(f"🔴 **Destino:** {destino}\n\n*Ponto de Referência:* {dest_ref if dest_ref else 'Paragem Urbana'}")

    st.write(f"**Modo:** {modo_linha} | **Regime:** {tipo_dia} | **Consulta a partir de:** {horario_desejado.strftime('%H:%M')}")

    if origem == destino:
        st.warning("⚠️ A paragem de origem e de destino são idênticas. Selecione paragens diferentes.")
    else:
        trips_c1, valid_c1 = calculate_next_trips("C1", tipo_dia, origem, destino, horario_desejado, n_horarios)
        trips_c2, valid_c2 = calculate_next_trips("C2", tipo_dia, origem, destino, horario_desejado, n_horarios)

        if modo_linha == "⚡ Comparar C1 e C2 (Mais Rápida)":
            st.markdown("### ⚡ Comparador Inteligente: C1 vs C2")

            if not trips_c1 and not trips_c2:
                st.info("ℹ️ Não foram encontradas viagens para nenhuma das linhas com as paragens e regime selecionados.")
            else:
                best_line = None
                time_saved = 0
                
                arr_c1 = trips_c1[0]["Chegada TD"] if trips_c1 else None
                arr_c2 = trips_c2[0]["Chegada TD"] if trips_c2 else None
                
                if arr_c1 and arr_c2:
                    diff_min = int(abs((arr_c1.total_seconds() - arr_c2.total_seconds()) // 60))
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
                        st.warning("Sem rotas na C1 para este regime de dia.")

                with col_c2:
                    st.markdown("#### 🚌 Linha C2 (Circular)")
                    if trips_c2:
                        st.metric("Próxima Chegada", trips_c2[0]["Chegada ao Destino"], delta=f"Partida: {trips_c2[0]['Partida da Origem']}")
                        st.dataframe(pd.DataFrame(trips_c2)[["Partida da Origem", "Chegada ao Destino", "Tempo Restante", "Duração Estimada"]], use_container_width=True)
                    else:
                        st.warning("Sem rotas na C2 para este regime de dia.")

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

                st.markdown(f"### 📋 Próximos {len(trips)} Horários - Linha {active_line} ({tipo_dia})")
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

with tab_mapa:
    target_map_line = "C1" if modo_linha == "Linha C1" else "C2"
    st.subheader(f"🗺️ Mapa do Circuito Urbano - Linha {target_map_line}")
    
    map_stops = st.session_state["stops_c1"] if target_map_line == "C1" else st.session_state["stops_c2"]
    map_data = []
    path_coords = []
    
    for s_name, s_off, s_lat, s_lon in map_stops:
        path_coords.append([s_lon, s_lat])
        
        if s_name == origem:
            color = [0, 200, 80, 220]
            radius = 120
        elif s_name == destino:
            color = [230, 40, 40, 220]
            radius = 120
        else:
            color = [30, 120, 220, 160]
            radius = 65
            
        ref_text = PONTOS_REFERENCIA.get(s_name, "")
        tooltip_name = f"{s_name} ({ref_text})" if ref_text else s_name
        
        map_data.append({
            "name": tooltip_name,
            "lat": s_lat,
            "lon": s_lon,
            "color": color,
            "radius": radius
        })
        
    df_map = pd.DataFrame(map_data)
    
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius="radius",
        pickable=True
    )
    
    path_data = [{"path": path_coords}]
    path_layer = pdk.Layer(
        "PathLayer",
        data=path_data,
        get_path="path",
        get_color=[0, 100, 200, 180],
        width_min_pixels=3
    )
    
    view_state = pdk.ViewState(
        latitude=40.6600,
        longitude=-7.9120,
        zoom=13,
        pitch=0
    )
    
    r = pdk.Deck(
        layers=[path_layer, scatter_layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}"}
    )
    
    st.pydeck_chart(r)
    st.caption("🟢 Verde: Origem | 🔴 Vermelho: Destino | 🔵 Azul: Outras paragens | ➖ Linha azul: Rota do circuito")

with tab_detalhes:
    st.subheader("📱 Visão Mobile Compacta")
    st.markdown("Visualização otimizada em cartões interativos para ecrãs de smartphone.")
    
    active_trips = trips_c1 if (modo_linha != "Linha C2" and trips_c1) else trips_c2
    active_line_name = "C1" if (modo_linha != "Linha C2" and trips_c1) else "C2"
    
    if origem != destino and active_trips:
        st.write(f"**Exibindo viagem na Linha {active_line_name} ({tipo_dia}):**")
        for idx, trip in enumerate(active_trips, 1):
            with st.expander(f"🚌 Opção #{idx}: {trip['Partida da Origem']} ➔ {trip['Chegada ao Destino']} ({trip['Tempo Restante']})", expanded=(idx==1)):
                st.write(f"• **Partida ({origem}):** {trip['Partida da Origem']}")
                st.write(f"• **Chegada ({destino}):** {trip['Chegada ao Destino']}")
                st.write(f"• **Tempo Restante:** {trip['Tempo Restante']}")
                st.write(f"• **Duração do Percurso:** {trip['Duração Estimada']}")
                st.write(f"• **Partida do Terminal:** {trip['Saída Terminal']}")

st.markdown("---")
st.caption("MUViseu Circulares v7 - Sistema de Horários & Mobilidade Urbana de Viseu.")
