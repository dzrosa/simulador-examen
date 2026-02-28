import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Simulador de Examen", page_icon="🎓", layout="centered")

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    .pregunta-texto { font-size: 18px !important; font-weight: 600; margin-bottom: 15px; line-height: 1.3; }
    .opcion-resultado {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 16px;
        border: 1px solid #dee2e6;
    }
    .correcta { background-color: #d4edda; color: #155724; border-color: #c3e6cb; font-weight: bold; }
    .incorrecta { background-color: #f8d7da; color: #721c24; border-color: #f5c6cb; }
    .neutral { background-color: #f1f3f5; color: #6c757d; opacity: 0.7; }
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
    except:
        return None

# --- INICIALIZACIÓN DE VARIABLES ---
if 'examen_iniciado' not in st.session_state:
    st.session_state.examen_iniciado = False
    st.session_state.indice_actual = 0
    st.session_state.aciertos = 0
    st.session_state.respondido = False
    st.session_state.finalizado = False
    st.session_state.preguntas_examen = []
    st.session_state.eleccion = None

df = load_data()

# --- VISTA: INICIO ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🎓 Simulador de Examen")
    if df is not None:
        st.write(f"Preguntas disponibles: **{len(df)}**")
        if st.button("🚀 COMENZAR EXAMEN", use_container_width=True, type="primary"):
            cantidad = min(60, len(df))
            indices = random.sample(range(len(df)), cantidad)
            st.session_state.preguntas_examen = df.iloc[indices].to_dict('records')
            st.session_state.examen_iniciado = True
            st.rerun()

# --- VISTA: RESULTADOS ---
elif st.session_state.finalizado:
    st.title("🏁 Resultados")
    st.metric("Aciertos", f"{st.session_state.aciertos} / {len(st.session_state.preguntas_examen)}")
    if st.button("🔄 Intentar de nuevo", use_container_width=True):
        st.session_state.examen_iniciado = False
        st.session_state.finalizado = False
        st.session_state.indice_actual = 0
        st.session_state.aciertos = 0
        st.rerun()

# --- VISTA: EXAMEN ---
elif st.session_state.examen_iniciado:
    total = len(st.session_state.preguntas_examen)
    actual = st.session_state.indice_actual
    pregunta = st.session_state.preguntas_examen[actual]
    correcta_val = str(pregunta['Respuesta Correcta']).strip()
    
    st.progress((actual) / total)
    st.write(f"Pregunta {actual + 1} de {total}")
    st.markdown(f'<p class="pregunta-texto">{pregunta["Pregunta"]}</p>', unsafe_allow_html=True)
    
    opciones = [str(pregunta['A']), str(pregunta['B']), str(pregunta['C']), str(pregunta['D'])]
    
    if not st.session_state.respondido:
        for idx, opcion in enumerate(opciones):
            if st.button(opcion, key=f"op_{actual}_{idx}", use_container_width=True):
                st.session_state.respondido = True
                st.session_state.eleccion = opcion.strip()
                if st.session_state.eleccion == correcta_val:
                    st.session_state.aciertos += 1
                st.rerun()
    else:
        for opcion in opciones:
            op_limpia = opcion.strip()
            if op_limpia == correcta_val:
                st.markdown(f'<div class="opcion-resultado correcta">✅ {opcion}</div>', unsafe_allow_html=True)
            elif op_limpia == st.session_state.eleccion:
                st.markdown(f'<div class="opcion-resultado incorrecta">❌ {opcion}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="opcion-resultado neutral">{opcion}</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="explicacion-caja"><b>💡 Explicación:</b><br>{pregunta["Explicación"]}</div>', unsafe_allow_html=True)
        
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
            if actual + 1 < total:
                st.session_state.indice_actual += 1
                st.session_state.respondido = False
                st.session_state.eleccion = None
                st.rerun()
            else:
                st.session_state.finalizado = True
                st.rerun()
