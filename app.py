import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Simulador de Examen", page_icon="🎓")

# --- CONFIGURACIÓN ---
# Verifica que este ID sea el correcto de tu Excel
SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        # Forzamos la lectura sin caché si hay problemas
        data = pd.read_csv(CSV_URL)
        data.columns = [c.strip() for c in data.columns]
        return data
    except Exception as e:
        st.error(f"⚠️ Error al conectar con Google Sheets: {e}")
        return None

st.title("🚀 Simulador de Examen")

df = load_data()

if df is not None:
    if 'examen_iniciado' not in st.session_state:
        st.session_state.examen_iniciado = False
        st.session_state.indice_actual = 0
        st.session_state.aciertos = 0
        st.session_state.respondido = False
        st.session_state.finalizado = False

    if not st.session_state.examen_iniciado:
        st.write(f"Preguntas disponibles: **{len(df)}**")
        if st.button("COMENZAR EXAMEN", use_container_width=True, type="primary"):
            cantidad = min(60, len(df))
            indices = random.sample(range(len(df)), cantidad)
            st.session_state.preguntas_examen = df.iloc[indices].to_dict('records')
            st.session_state.examen_iniciado = True
            st.rerun()
    
    elif st.session_state.finalizado:
        st.header("🏁 Fin del examen")
        st.metric("Aciertos", st.session_state.aciertos)
        if st.button("Reiniciar"):
            st.session_state.examen_iniciado = False
            st.rerun()
    
    else:
        # Lógica de preguntas simplificada para probar carga
        actual = st.session_state.indice_actual
        pregunta = st.session_state.preguntas_examen[actual]
        st.write(f"Pregunta {actual + 1}")
        st.subheader(pregunta['Pregunta'])
        if st.button("Siguiente (Prueba)"):
            st.session_state.indice_actual += 1
            st.rerun()
else:
    st.warning("No se pudieron cargar los datos. Revisa si el Google Sheet está compartido como 'Cualquier persona con el enlace'.")
