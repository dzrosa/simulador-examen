import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Simulador de Examen PRO", page_icon="🎓", layout="centered")

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
        st.error(f"Error al conectar con los datos: {e}")
        return None

# --- INICIALIZACIÓN DE ESTADO ---
if 'examen_iniciado' not in st.session_state:
    st.session_state.update({
        'examen_iniciado': False,
        'indice_actual': 0,
        'aciertos': 0,
        'respondido': False,
        'finalizado': False,
        'preguntas_examen': []
    })

df = load_data()

# --- VISTA: INICIO ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🎓 Simulador de Examen Profesional")
    if df is not None:
        st.write(f"Banco de preguntas detectado: **{len(df)}**")
        st.info("El examen consta de 60 preguntas al azar. Necesitas 36 aciertos para aprobar.")
        if st.button("🚀 COMENZAR EXAMEN", use_container_width=True, type="primary"):
            cantidad = min(60, len(df))
            indices = random.sample(range(len(df)), cantidad)
            st.session_state.preguntas_examen = df.iloc[indices].to_dict('records')
            st.session_state.examen_iniciado = True
            st.rerun()

# --- VISTA: RESULTADOS ---
elif st.session_state.finalizado:
    st.title("🏁 Resultados Finales")
    total_intentadas = st.session_state.indice_actual + (1 if st.session_state.respondido else 0)
    nota = (st.session_state.aciertos / total_intentadas * 10) if total_intentadas > 0 else 0
    
    col1, col2 = st.columns(2)
    col1.metric("Aciertos", f"{st.session_state.aciertos}")
    col2.metric("Nota Estimada", f"{nota:.1f}/10")

    if st.session_state.aciertos >= 36:
        st.success("🎉 ¡APROBADO! Has superado el mínimo de 36 aciertos.")
    else:
        st.error(f"❌ REPROBADO. Tienes {st.session_state.aciertos} aciertos (Mínimo: 36).")
    
    if st.button("🔄 Intentar otro examen", use_container_width=True):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()

# --- VISTA: EXAMEN EN CURSO ---
elif st.session_state.examen_iniciado:
    total = len(st.session_state.preguntas_examen)
    actual = st.session_state.indice_actual
    pregunta = st.session_state.preguntas_examen[actual]
    
    st.progress((actual) / total)
    st.subheader(f"Pregunta {actual + 1} de {total}")
    st.markdown(f"### {pregunta['Pregunta']}")
    
    # Opciones
    opciones = [str(pregunta['A']), str(pregunta['B']), str(pregunta['C']), str(pregunta['D'])]
    
    for idx, opcion in enumerate(opciones):
        if st.button(opcion, key=f"btn_{actual}_{idx}", disabled=st.session_state.respondido, use_container_width=True):
            st.session_state.respondido = True
            correcta = str(pregunta['Respuesta Correcta']).strip()
            if opcion.strip() == correcta:
                st.session_state.aciertos += 1
                st.success("¡Correcto! 🎉")
            else:
                st.error(f"Incorrecto. La respuesta era: {correcta}")
            st.info(f"**Explicación:** {pregunta['Explicación']}")

    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        if st.session_state.respondido:
            label_sig = "Siguiente ➡️" if actual + 1 < total else "Ver Resultados 🏁"
            if st.button(label_sig, use_container_width=True, type="primary"):
                if actual + 1 < total:
                    st.session_state.indice_actual += 1
                    st.session_state.respondido = False
                    st.rerun()
                else:
                    st.session_state.finalizado = True
                    st.session_state.examen_iniciado = False
                    st.rerun()
    with c2:
        if st.button("⏹️ Finalizar ahora", use_container_width=True, help="Termina el examen con lo que llevas"):
            st.session_state.finalizado = True
            st.session_state.examen_iniciado = False
            st.rerun()
