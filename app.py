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
    st.title("🔒 Acceso Exclusivo")
    email_user = st.text_input("Correo electrónico:").lower().strip()
    clave_user = st.text_input("Clave de acceso (PIN):", type="password").strip()
    if st.button("Validar Credenciales", use_container_width=True, type="primary"):
        if df_usuarios is not None:
            user_match = df_usuarios[df_usuarios['email'] == email_user]
            if not user_match.empty and str(user_match.iloc[0]['clave']).strip() == clave_user:
                st.session_state.acceso_concedido = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")
    st.stop()

# --- VARIABLES DE ESTADO ---
if 'examen_iniciado' not in st.session_state:
    st.session_state.update({'examen_iniciado': False, 'finalizado': False, 'indice_actual': 0, 'aciertos': 0, 'respondido': False, 'preguntas_examen': [], 'inicio_tiempo': 0, 'eleccion': None})

# --- VISTA 1: CONFIGURACIÓN ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🚀 Panel de Estudio")
    if df_preguntas is not None:
        lista_clases = sorted(df_preguntas['Clase'].unique().tolist())
        
        st.markdown("### 1. Selecciona las unidades que quieres practicar:")
        # Usamos st.pills para una selección múltiple mucho más visual
        clases_sel = st.pills("Puedes marcar varias unidades simultáneamente:", options=lista_clases, selection_mode="multi")
        
        if not clases_sel:
            st.info("💡 No has seleccionado ninguna unidad. Se incluirán **todas las preguntas** del examen.")
            df_f = df_preguntas
        else:
            df_f = df_preguntas[df_preguntas['Clase'].isin(clases_sel)]
            st.success(f"Seleccionadas: {', '.join(map(str, clases_sel))}")
        
        st.metric("Preguntas disponibles", len(df_f))
        
        if st.button("🚀 COMENZAR EXAMEN", use_container_width=True, type="primary"):
            pool = df_f.to_dict('records')
            random.shuffle(pool)
            st.session_state.preguntas_examen = pool[:60]
            st.session_state.inicio_tiempo = time.time()
            st.session_state.examen_iniciado = True
            st.session_state.indice_actual = 0
            st.session_state.aciertos = 0
            st.rerun()

# --- VISTA 2: EXAMEN ---
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
    
    col_header, col_timer = st.columns([2, 1])
    with col_header:
        st.write(f"Pregunta **{actual + 1}** de {total}")
        st.caption(f"Unidad: {pregunta['Clase']}")
    with col_timer:
        st.markdown(f'<p class="timer-caja">⏳ {h:02d}:{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
    
    st.progress((actual) / total)
    
    # Botón para salir
    if st.button("🏁 Entregar examen ahora", type="secondary"):
        st.session_state.finalizado = True
        st.rerun()

    st.markdown("---")
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
            if op_s == correcta_val:
                st.markdown(f'<div class="opcion-resultado correcta">✅ {op}</div>', unsafe_allow_html=True)
            elif op_s == st.session_state.eleccion:
                st.markdown(f'<div class="opcion-resultado incorrecta">❌ {op}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="opcion-resultado neutral">{op}</div>', unsafe_allow_html=True)
        
        st.info(f"💡 **Explicación:** {pregunta['Explicación']}")
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
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
    total_vistas = st.session_state.indice_actual + (1 if st.session_state.respondido else 0)
    st.metric("Aciertos", f"{st.session_state.aciertos} / {total_vistas}")
    if st.button("🔄 Nuevo examen"):
        st.session_state.examen_iniciado = False
        st.session_state.finalizado = False
        st.rerun()
