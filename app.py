import streamlit as st
import pandas as pd
import random
import time

# Configuración inicial
st.set_page_config(page_title="Simulador Premium - Biología", page_icon="🎓", layout="centered")

# --- CARGA DE DATOS ---
SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
GID_USUARIOS = "1819383994"

@st.cache_data(ttl=10)
def load_all_data():
    try:
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        df_p = pd.read_csv(url_p)
        df_p.columns = [c.strip() for c in df_p.columns]
        url_u = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_USUARIOS}"
        df_u = pd.read_csv(url_u)
        df_u.columns = [c.strip().lower() for c in df_u.columns]
        return df_p, df_u
    except:
        return None, None

df_preguntas, df_usuarios = load_all_data()

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .pregunta-texto { font-size: 18px !important; font-weight: bold; margin-bottom: 20px; }
    .opcion-resultado { padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #dee2e6; }
    .correcta { background-color: #d4edda; color: #155724; font-weight: bold; }
    .incorrecta { background-color: #f8d7da; color: #721c24; }
    .neutral { background-color: #f1f3f5; color: #6c757d; }
    .timer-caja { font-size: 22px; font-weight: bold; color: #d9534f; text-align: right; background: #fff5f5; padding: 5px 10px; border-radius: 5px; border: 1px solid #d9534f; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
if 'acceso_concedido' not in st.session_state:
    st.session_state.acceso_concedido = False

if not st.session_state.acceso_concedido:
    st.title("🔒 Acceso Exclusivo - Biología")
    st.write("Ingresa tus credenciales para comenzar el simulacro.")
    email_user = st.text_input("Correo electrónico:").lower().strip()
    clave_user = st.text_input("Clave de acceso (PIN):", type="password").strip()
    if st.button("Validar Credenciales", use_container_width=True, type="primary"):
        if df_usuarios is not None:
            user_match = df_usuarios[df_usuarios['email'] == email_user]
            if not user_match.empty:
                clave_correcta = str(user_match.iloc[0]['clave']).strip()
                if clave_user == clave_correcta:
                    st.session_state.acceso_concedido = True
                    st.rerun()
                else:
                    st.error("La clave ingresada es incorrecta.")
            else:
                st.error("El correo no se encuentra registrado.")
        else:
            st.error("Error al conectar con la base de datos.")
    st.stop()

# --- INICIALIZACIÓN DE VARIABLES DEL EXAMEN ---
if 'examen_iniciado' not in st.session_state:
    st.session_state.examen_iniciado = False
    st.session_state.finalizado = False
    st.session_state.indice_actual = 0
    st.session_state.aciertos = 0
    st.session_state.respondido = False
    st.session_state.preguntas_examen = []
    st.session_state.inicio_tiempo = 0
    st.session_state.eleccion = None

# --- VISTAS DEL EXAMEN ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🚀 Prepárate para el examen")
    if df_preguntas is not None:
        lista_clases = sorted(df_preguntas['Clase'].unique().tolist())
        clase_sel = st.selectbox("Selecciona tu unidad de estudio:", ["Todas las Clases"] + lista_clases)
        df_f = df_preguntas if clase_sel == "Todas las Clases" else df_preguntas[df_preguntas['Clase'] == clase_sel]
        if st.button("COMENZAR SIMULACRO", use_container_width=True, type="primary"):
            pool = df_f.to_dict('records')
            random.shuffle(pool)
            st.session_state.preguntas_examen = pool[:60]
            st.session_state.inicio_tiempo = time.time()
            st.session_state.examen_iniciado = True
            st.rerun()

elif st.session_state.examen_iniciado and not st.session_state.finalizado:
    restante = 5400 - (time.time() - st.session_state.inicio_tiempo)
    if restante <= 0:
        st.session_state.finalizado = True
        st.rerun()
    m, s = divmod(int(restante), 60)
    h, m = divmod(m, 60)
    actual = st.session_state.indice_actual
    total = len(st.session_state.preguntas_examen)
    pregunta = st.session_state.preguntas_examen[actual]
    c1, c2 = st.columns([2, 1])
    with c1: st.write(f"Pregunta {actual + 1} de {total}")
    with c2: st.markdown(f'<p class="timer-caja">⏳ {h:02d}:{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
    st.progress(actual / total)
    st.markdown(f'<p class="pregunta-texto">{pregunta["Pregunta"]}</p>', unsafe_allow_html=True)
    opciones = [str(pregunta['Opción A']), str(pregunta['Opción B']), str(pregunta['Opción C']), str(pregunta['Opción D'])]
    correcta_val = str(pregunta['Opción Correcta']).strip()
    if not st.session_state.respondido:
        for idx, op in enumerate(opciones):
            if st.button(op, key=f"q_{actual}_{idx}", use_container_width=True):
                st.session_state.eleccion = op.strip()
                st.session_state.respondido = True
                if st.session_state.eleccion == correcta_val:
                    st.session_state.aciertos += 1
                st.rerun()
        time.sleep(1)
        st.rerun()
    else:
        for op in opciones:
            op_s = op.strip()
            if op_s == correcta_val: st.markdown(f'<div class="opcion-resultado correcta">✅ {op}</div>', unsafe_allow_html=True)
            elif op_s == st.session_state.eleccion: st.markdown(f'<div class="opcion-resultado incorrecta">❌ {op}</div>', unsafe_allow_html=True)
            else: st.markdown(f'<div class="opcion-resultado neutral">{op}</div>', unsafe_allow_html=True)
        st.info(f"💡 **Explicación:** {pregunta['Explicación']}")
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
            if actual + 1 < total:
                st.session_state.indice_actual += 1
                st.session_state.respondido = False
                st.rerun()
            else:
                st.session_state.finalizado = True
                st.rerun()

elif st.session_state.finalizado:
    st.title("🏁 Resultados Finales")
    st.metric("Aciertos", f"{st.session_state.aciertos} / {len(st.session_state.preguntas_examen)}")
    if st.button("🔄 Volver al Inicio"):
        st.session_state.examen_iniciado = False
        st.session_state.finalizado = False
        st.rerun()
