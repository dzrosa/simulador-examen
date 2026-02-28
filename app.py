import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="Simulador de Examen", page_icon="🎓", layout="centered")

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    .pregunta-texto { font-size: 18px !important; font-weight: 600; margin-bottom: 15px; line-height: 1.3; }
    .opcion-resultado { padding: 12px; border-radius: 8px; margin-bottom: 8px; font-size: 16px; border: 1px solid #dee2e6; }
    .correcta { background-color: #d4edda; color: #155724; border-color: #c3e6cb; font-weight: bold; }
    .incorrecta { background-color: #f8d7da; color: #721c24; border-color: #f5c6cb; }
    .neutral { background-color: #f1f3f5; color: #6c757d; opacity: 0.7; }
    .explicacion-caja { font-size: 18px !important; background-color: #e9f5ff; padding: 15px; border-radius: 10px; color: #0c5460; border-left: 5px solid #17a2b8; margin-top: 20px; }
    /* Estilo para el cronómetro */
    .timer-caja { font-size: 20px; font-weight: bold; color: #d9534f; text-align: right; margin-bottom: 10px; }
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

# --- INICIALIZACIÓN ---
if 'examen_iniciado' not in st.session_state:
    st.session_state.examen_iniciado = False
    st.session_state.indice_actual = 0
    st.session_state.aciertos = 0
    st.session_state.respondido = False
    st.session_state.finalizado = False
    st.session_state.preguntas_examen = []
    st.session_state.eleccion = None
    st.session_state.inicio_tiempo = None

df = load_data()

# --- VISTA: INICIO ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🎓 Simulador de Examen")
    if df is not None:
        st.write(f"Preguntas disponibles: **{len(df)}**")
        st.write("⏱️ Tiempo límite: **1 hora y 30 minutos**")
        if st.button("🚀 COMENZAR EXAMEN", use_container_width=True, type="primary"):
            cantidad = min(60, len(df))
            indices = random.sample(range(
