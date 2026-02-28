import streamlit as st
import pandas as pd
import random
import time

# Configuración de página al inicio
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
    .timer-caja { font-size: 20px; font-weight: bold; color: #d9534f; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(CSV_URL)
        data.columns = [c.strip() for c in data.columns]
        return data
    except:
        return None

# --- INICIALIZACIÓN DE VARIABLES (SESSION STATE) ---
if 'examen_iniciado' not in st.session_state:
    st.session_state.examen_iniciado = False
if 'finalizado' not in st.session_state:
    st.session_state.finalizado = False
if 'indice_actual' not in st.session_state:
    st.session_state.indice_actual = 0
if 'aciertos' not in st.session_state:
    st.session_state.aciertos = 0
if 'respondido' not in st.session_state:
    st.session_state.respondido = False
if 'preguntas_examen' not in st.session_state:
    st.session_state.preguntas_examen = []
if 'eleccion' not in st.session_state:
    st.session_state.eleccion = None
if 'inicio_tiempo' not in st.session_state:
    st.session_state.inicio_tiempo = None

df = load_data()

# --- VISTA 1: PANTALLA DE INICIO ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🎓 Simulador de Examen")
    if df is not None:
        st.write(f"Preguntas disponibles en base: **{len(df)}**")
        st.info("⏱️ Tienes **1 hora y 30 minutos** para completar 60 preguntas.")
        
        if st.button("🚀 COMENZAR EXAMEN", use_container_width=True, type="primary"):
            # Generar preguntas
            pool = df.to_dict('records')
            cantidad = min(60, len(pool))
            st.session_state.preguntas_examen = random.sample(pool, cantidad)
            
            # Marcar inicio
            st.session_state.inicio_tiempo = time.time()
            st.session_state.examen_iniciado = True
            st.session_state.indice_actual = 0
            st.session_state.aciertos = 0
            st.rerun()
    else:
        st.error("No se pudo cargar el Excel. Revisa el link y los permisos.")

# --- VISTA 2: RESULTADOS ---
elif st.session_state.finalizado:
    st.title("🏁 Examen Finalizado")
    total_p = len(st.session_state.preguntas_examen)
    st.metric("Puntaje Final", f"{st.session_state.aciertos} / {total_p}")
    
    if st.button("🔄 Volver al Inicio", use_container_width=True):
        st.session_state.examen_iniciado = False
