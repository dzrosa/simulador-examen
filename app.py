import streamlit as st
import pandas as pd
import random
import time

# Configuración inicial
st.set_page_config(page_title="Simulador Premium - Biología 91", page_icon="🎓", layout="centered")

# --- TEMARIO EXTRAÍDO DEL PDF ---
TEMARIO = {
    "1": "Características de los seres vivos y Teoría celular",
    "2": "Estructura atómica, Agua y pH",
    "3": "Biomoléculas: Glúcidos, Lípidos y Ácidos Nucleicos",
    "4": "Proteínas: Estructura y Función",
    "5": "Bioenergética, Metabolismo y Enzimas",
    "6": "Organización celular (Procariotas y Eucariotas)",
    "7": "Membranas celulares y Transporte",
    "8": "Sistema de endomembranas",
    "9": "Digestión celular y Peroxisomas",
    "10": "Mitocondrias, Cloroplastos y Respiración Celular",
    "11": "Fotosíntesis",
    "12": "Citoesqueleto y Movilidad celular",
    "13": "Núcleo y Cromatina",
    "14": "Transcripción del ADN y ARN",
    "15": "Traducción y Código genético",
    "16": "Clasificación de Proteínas y Tráfico",
    "17": "Señalización celular",
    "18": "Ciclo celular y Control",
    "19": "Replicación del ADN y Mutaciones",
    "20": "Mitosis y Citocinesis",
    "21": "Meiosis y Crossing-over"
}

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
    /* Estilo para que las Pills se vean mejor en móviles */
    div[data-testid="stPills"] button { white-space: normal !important; text-align: left !important; height: auto !important; padding: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
if 'acceso_concedido' not in st.session_state:
    st.session_state.acceso_concedido = False

if not st.session_state.acceso_concedido:
    st.title("🔒 Acceso Exclusivo")
    email_user = st.text_input("Correo electrónico:").lower().strip()
    clave_user = st.text_input("PIN de acceso:", type="password").strip()
    if st.button("Ingresar", use_container_width=True, type="primary"):
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
        
        # Limpieza y ordenamiento numérico
        df_preguntas['Clase_ID'] = pd.to_numeric(df_preguntas['Clase'], errors='coerce')
        clases_num = sorted(df_preguntas['Clase_ID'].dropna().unique().astype(int))
        
        opciones_visuales = [f"Clase {c}: {TEMARIO.get(str(c), 'Tema de repaso')}" for c in clases_num]
        
        st.markdown("### 1. Elige qué quieres estudiar hoy:")
        
        # INTENTO DE PILLS CON FALLBACK (Si falla, usa multiselect automáticamente)
        try:
            seleccion_visual = st.pills(
                "Selecciona una o varias unidades (se marcarán en azul):",
                options=opciones_visuales,
                selection_mode="multi"
            )
        except AttributeError:
            # Si la versión de Streamlit es vieja y no tiene .pills, usamos esto:
            seleccion_visual = st.multiselect(
                "Selecciona las unidades:",
                options=opciones_visuales
            )
        
        # Procesar selección
        clases_finales = [s.split(":")[0].replace("Clase ", "").strip() for s in (seleccion_visual or [])]
        
        if not clases_finales:
            df_f = df_preguntas
            st.info("💡 No seleccionaste nada. Se incluirán **todas las clases**.")
        else:
            df_f = df_preguntas[df_preguntas['Clase_ID'].astype(str).str.split('.').str[0].isin(clases_finales)]
            st.success(f"Unidades seleccionadas: {', '.join(clases_finales)}")
        
        st.metric("Preguntas disponibles", len(df_f))
        
        if st.button("🚀 COMENZAR EXAMEN", use_container_width=True, type="primary"):
            if len(df_f) > 0:
                pool = df_f.to_dict('records')
                random.shuffle(pool)
                st.session_state.preguntas_examen = pool[:60]
                st.session_state.inicio_tiempo = time.time()
                st.session_state.examen_iniciado = True
                st.session_state.indice_actual = 0
                st.session_state.aciertos = 0
                st.rerun()
            else:
                st.error("No hay preguntas en esta selección.")

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
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.write(f"Pregunta **{actual + 1}** de {total}")
        cid = str(pregunta['Clase']).split('.')[0]
        st.caption(f"Unidad {cid}: {TEMARIO.get(cid, 'Repaso')}")
    with c2:
        st.markdown(f'<p class="timer-caja">⏳ {h:02d}:{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
    
    st.progress((actual) / total)
    
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
