import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Simulador de Examen", page_icon="🎓", layout="centered")

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    .pregunta-texto { font-size: 18px !important; font-weight: 600; margin-bottom: 15px; line-height: 1.3; }
    
    /* Estilos de las tarjetas de respuesta reveladas */
    .opcion-resultado {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 16px;
        border: 1px solid transparent;
    }
    .correcta {
        background-color: #d4edda;
        color: #155724;
        border-color: #c3e6cb;
        font-weight: bold;
    }
    .incorrecta {
        background-color: #f8d7da;
        color: #721c24;
        border-color: #f5c6cb;
    }
    .neutral {
        background-color: #f1f3f5;
        color: #6c757d;
        border-color: #dee2e6;
        opacity: 0.7;
    }
    
    .explicacion-caja {
        font-size: 18px !important;
        background-color: #e9f5ff;
        padding: 15px;
        border-radius: 10px;
        color: #0c5460;
        border-left: 5px solid #17a2b8;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        data = pd.read_csv(CSV_URL)
        data.columns = [c.strip() for c in data.columns]
        return data
    except: return None

if 'examen_iniciado' not in st.session_state:
    st.session_state.update({'examen_iniciado': False, 'indice_actual': 0, 'aciertos': 0, 'respondido': False, 'finalizado': False, 'preguntas_examen': [], 'eleccion': None})

df = load_data()

# --- VISTA: INICIO ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🎓 Simulador de Examen")
    if st.button("🚀 COMENZAR EXAMEN", use_container_width=True, type="primary"):
        indices = random.sample(range(len(df)), min(
