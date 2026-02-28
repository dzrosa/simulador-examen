import streamlit as st
import pandas as pd
import random
import time

# Configuración inicial
st.set_page_config(page_title="Simulador Premium - Examen", page_icon="🎓", layout="centered")

# --- CARGA DE DATOS ---
SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
GID_USUARIOS = "1819383994"

@st.cache_data(ttl=10) # Se actualiza cada 10 segundos para nuevos pagos
def load_all_data():
    try:
        # URL de Preguntas (Hoja 1 - gid 0)
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        df_p = pd.read_csv(url_p)
        df_p.columns = [c.strip() for c in df_p.columns]
        
        # URL de Usuarios (Hoja Usuarios - tu gid)
        url_u = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_USUARIOS}"
        df_u = pd.read_csv(url_u)
        df_u.columns = [c.strip() for c in df_u.columns]
        
        return df_p, df_u
    except Exception as e:
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

# --- SISTEMA DE MURO DE PAGO ---
if 'acceso_concedido' not in st.session_state:
    st.session_state.acceso_concedido = False

if not st.session_state.acceso_concedido:
    st.title("🔒 Simulador Examen Premium")
    st.write("Bienvenido al simulador actualizado. Por favor, ingresa tu correo para continuar.")
    
    email_input = st.text_input("Correo electrónico registrado:").lower().strip()
    
    if st.button("Ingresar al Simulador", use_container_width=True, type="primary"):
        if df_usuarios is not None and email_input in df_usuarios['Email'].str.lower().values:
            st.session_state.acoceso_concedido = True # Pequeño seguro contra refrescos
            st.session_state.acceso_concedido = True
            st.success("¡Acceso autorizado!")
            st.rerun()
        else:
            st.error("Acceso denegado. Este correo no está en nuestra lista de alumnos activos.")
            st.info("💡 **¿Todavía no tienes acceso?** Envía tu comprobante de pago por WhatsApp para ser habilitado de inmediato.")
            st.markdown("[👉 Contactar Soporte / Comprar Acceso](https://wa.me/TUNUMERO)") # CAMBIA ESTO POR TU LINK
    st.stop()

# --- INICIALIZACIÓN DE VARIABLES DEL EXAMEN ---
if 'examen_iniciado' not in st.session_state:
    st.session_state.update({
        'examen_iniciado': False,
        'finalizado': False,
        'indice_actual': 0,
        'aciertos': 0,
        'respondido': False,
        'preguntas_examen': [],
        'inicio_tiempo': 0,
        'eleccion': None
    })

# --- VISTA 1: CONFIGURACIÓN E INICIO ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🎓 Configuración del Examen")
    
    if df_preguntas is not None:
        lista_clases = sorted(df_preguntas['Clase'].unique().tolist())
        opciones = ["Todas las Clases"] + lista_clases
        clase_sel = st.selectbox("Selecciona qué deseas estudiar:", opciones)
        
        df_f = df_preguntas if clase_sel == "Todas las Clases" else df_preguntas[df_preguntas['Clase'] == clase_sel]
        
        st.write(f"Preguntas disponibles: **{len(df_f)}**")
        
        if st.button("🚀 COMENZAR SIMULACRO", use_container_width=True, type="primary"):
            pool = df_f.to_dict('records')
            random.shuffle(pool)
            st.session_state.preguntas_examen = pool[:60]
            st.session_state.inicio_tiempo = time.time()
            st.session_state.examen_iniciado = True
            st.session_state.indice_actual = 0
            st.session_state.aciertos = 0
            st.session_state.respondido = False
            st.rerun()

# --- VISTA 2: EXAMEN EN CURSO ---
elif st.session_state.examen_iniciado and not st.session_state.finalizado:
    # Tiempo: 1h 30min = 5400 seg
    restante = 5400 - (time.time() - st.session_state.inicio_tiempo)

    if restante <= 0:
        st.session_state.finalizado = True
        st.rerun()

    m, s = divmod(int(restante), 60)
    h, m = divmod(m, 60)
    
    actual = st.session_state.indice_actual
    total = len(st.session_state.preguntas_examen)
    pregunta = st.session_state.preguntas_examen[actual]
    
    # Header
    c1, c2 = st.columns([2, 1])
    with c1: 
        st.write(f"Pregunta {actual + 1} de {total}")
        st.caption(f"Tema: {pregunta['Tema']}")
    with c2: 
        st.markdown(f'<p class="timer-caja">⏳ {h:02d}:{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
    
    st.progress(actual / total)

    # Pregunta y Opciones
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
