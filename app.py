import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Simulador de Examen", page_icon="🎓", layout="centered")

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

# --- INICIALIZACIÓN ---
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
if 'inicio_tiempo' not in st.session_state:
    st.session_state.inicio_tiempo = 0

df = load_data()

# --- CSS ---
st.markdown("""
    <style>
    .pregunta-texto { font-size: 18px !important; font-weight: bold; margin-bottom: 20px; }
    .opcion-resultado { padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #dee2e6; }
    .correcta { background-color: #d4edda; color: #155724; }
    .incorrecta { background-color: #f8d7da; color: #721c24; }
    .neutral { background-color: #f1f3f5; color: #6c757d; }
    .timer-caja { font-size: 20px; font-weight: bold; color: #d9534f; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- VISTA 1: INICIO ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🎓 Simulador de Examen")
    if df is not None:
        st.write(f"Preguntas cargadas: {len(df)}")
        if st.button("🚀 COMENZAR EXAMEN", use_container_width=True, type="primary"):
            # Lógica simplificada al máximo
            pool = df.to_dict('records')
            random.shuffle(pool)
            st.session_state.preguntas_examen = pool[:60]
            st.session_state.inicio_tiempo = time.time()
            st.session_state.examen_iniciado = True
            st.session_state.indice_actual = 0
            st.session_state.aciertos = 0
            st.session_state.respondido = False
            st.rerun()
    else:
        st.error("Error cargando base de datos.")

# --- VISTA 2: EXAMEN ---
elif st.session_state.examen_iniciado and not st.session_state.finalizado:
    # Tiempo
    restante = 5400 - (time.time() - st.session_state.inicio_tiempo)
    if restante <= 0:
        st.session_state.finalizado = True
        st.rerun()

    m, s = divmod(int(restante), 60)
    h, m = divmod(m, 60)
    
    actual = st.session_state.indice_actual
    total = len(st.session_state.preguntas_examen)
    pregunta = st.session_state.preguntas_examen[actual]
    
    c1, c2 = st.columns([3, 1])
    with c1: st.write(f"Pregunta {actual + 1} de {total}")
    with c2: st.markdown(f'<p class="timer-caja">⏳ {h:02d}:{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
    
    st.progress(actual / total)
    st.markdown(f'<p class="pregunta-texto">{pregunta["Pregunta"]}</p>', unsafe_allow_html=True)
    
    opciones = [str(pregunta['A']), str(pregunta['B']), str(pregunta['C']), str(pregunta['D'])]
    correcta_val = str(pregunta['Respuesta Correcta']).strip()

    if not st.session_state.respondido:
        for idx, op in enumerate(opciones):
            if st.button(op, key=f"btn_{idx}", use_container_width=True):
                st.session_state.eleccion = op.strip()
                st.session_state.respondido = True
                if st.session_state.eleccion == correcta_val:
                    st.session_state.aciertos += 1
                st.rerun()
    else:
        for op in opciones:
            op_s = op.strip()
            if op_s == correcta_val:
                st.markdown(f'<div class="opcion-resultado correcta">✅ {op}</div>', unsafe_allow_html=True)
            elif op_s == st.session_state.eleccion:
                st.markdown(f'<div class="opcion-resultado incorrecta">❌ {op}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="opcion-resultado neutral">{op}</div>', unsafe_allow_html=True)
        
        st.info(f"💡 {pregunta['Explicación']}")
        
        if st.button("Siguiente ➡️", use_container_width=True, type="primary"):
            if actual + 1 < total:
                st.session_state.indice_actual += 1
                st.session_state.respondido = False
                st.rerun()
            else:
                st.session_state.finalizado = True
                st.rerun()

# --- VISTA 3: RESULTADOS ---
elif st.session_state.finalizado:
    st.title("🏁 Resultados")
    st.metric("Puntaje", f"{st.session_state.aciertos} / {len(st.session_state.preguntas_examen)}")
    if st.button("🔄 Reiniciar"):
        st.session_state.examen_iniciado = False
        st.session_state.finalizado = False
        st.rerun()
