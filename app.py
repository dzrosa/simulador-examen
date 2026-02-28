import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Simulador de Examen", page_icon="🎓", layout="centered")

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <style>
    /* Reducir espacio superior */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    
    /* Tamaño de la pregunta */
    .pregunta-texto {
        font-size: 18px !important;
        font-weight: 600;
        line-height: 1.2;
        margin-bottom: 10px;
    }
    
    /* Tamaño de la explicación */
    .explicacion-caja {
        font-size: 19px !important;
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        color: #1f77b4;
        border-left: 5px solid #1f77b4;
    }
    
    /* Compactar botones */
    .stButton > button {
        margin-bottom: -10px !important;
        padding: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE DATOS ---
SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        data = pd.read_csv(CSV_URL)
        data.columns = [c.strip() for c in data.columns]
        return data
    except Exception as e:
        st.error(f"Error: {e}")
        return None

if 'examen_iniciado' not in st.session_state:
    st.session_state.update({'examen_iniciado': False, 'indice_actual': 0, 'aciertos': 0, 'respondido': False, 'finalizado': False, 'preguntas_examen': []})

df = load_data()

# --- LÓGICA DE VISTAS ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🎓 Simulador")
    if df is not None:
        if st.button("🚀 COMENZAR EXAMEN", use_container_width=True, type="primary"):
            indices = random.sample(range(len(df)), min(60, len(df)))
            st.session_state.preguntas_examen = df.iloc[indices].to_dict('records')
            st.session_state.examen_iniciado = True
            st.rerun()

elif st.session_state.finalizado:
    st.title("🏁 Resultados")
    st.metric("Aciertos", f"{st.session_state.aciertos}")
    if st.button("🔄 Reiniciar"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

elif st.session_state.examen_iniciado:
    total = len(st.session_state.preguntas_examen)
    actual = st.session_state.indice_actual
    pregunta = st.session_state.preguntas_examen[actual]
    
    st.progress((actual) / total)
    st.write(f"Pregunta {actual + 1} de {total}")
    
    # Pregunta más pequeña usando la clase CSS
    st.markdown(f'<p class="pregunta-texto">{pregunta["Pregunta"]}</p>', unsafe_allow_html=True)
    
    opciones = [str(pregunta['A']), str(pregunta['B']), str(pregunta['C']), str(pregunta['D'])]
    
    for idx, opcion in enumerate(opciones):
        if st.button(opcion, key=f"b{actual}_{idx}", disabled=st.session_state.respondido, use_container_width=True):
            st.session_state.respondido = True
            correcta = str(pregunta['Respuesta Correcta']).strip()
            if opcion.strip() == correcta:
                st.session_state.aciertos += 1
                st.toast("¡Correcto!", icon="✅")
            st.rerun()

    if st.session_state.respondido:
        correcta = str(pregunta['Respuesta Correcta']).strip()
        # Explicación más grande y destacada
        st.markdown(f'<div class="explicacion-caja"><b>Respuesta: {correcta}</b><br>{pregunta["Explicación"]}</div>', unsafe_allow_html=True)
        
        st.write("") # Espacio
        if st.button("Siguiente ➡️", use_container_width=True, type="primary"):
            if actual + 1 < total:
                st.session_state.indice_actual += 1
                st.session_state.respondido = False
            else:
                st.session_state.finalizado = True
            st.rerun()
