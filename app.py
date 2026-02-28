import streamlit as st
import pandas as pd
import random
import time

# Configuración inicial
st.set_page_config(page_title="Simulador Premium - Biología 91", page_icon="🎓", layout="wide")

# --- TEMARIO COMPLETO ---
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
    .pregunta-texto { font-size: 20px !important; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .opcion-resultado { padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #E5E7EB; }
    .correcta { background-color: #D1FAE5; color: #065F46; border: 2px solid #10B981; }
    .incorrecta { background-color: #FEE2E2; color: #991B1B; border: 2px solid #EF4444; }
    .neutral { background-color: #F3F4F6; color: #374151; }
    .timer-caja { font-size: 24px; font-weight: bold; color: #B91C1C; background: #FEF2F2; padding: 10px; border-radius: 10px; border: 2px solid #FECACA; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'acceso_concedido' not in st.session_state:
    st.session_state.acceso_concedido = False

if not st.session_state.acceso_concedido:
    st.title("🔒 Acceso al Simulador")
    col1, col2 = st.columns(2)
    with col1:
        email_user = st.text_input("Correo electrónico:").lower().strip()
        clave_user = st.text_input("PIN:", type="password").strip()
        if st.button("Ingresar", use_container_width=True, type="primary"):
            if df_usuarios is not None:
                user_match = df_usuarios[df_usuarios['email'] == email_user]
                if not user_match.empty and str(user_match.iloc[0]['clave']).strip() == clave_user:
                    st.session_state.acceso_concedido = True
                    st.rerun()
                else: st.error("Datos incorrectos")
    st.stop()

# --- ESTADO ---
if 'examen_iniciado' not in st.session_state:
    st.session_state.update({'examen_iniciado': False, 'finalizado': False, 'indice_actual': 0, 'aciertos': 0, 'respondido': False, 'preguntas_examen': [], 'inicio_tiempo': 0, 'eleccion': None})

# --- VISTA 1: CONFIGURACIÓN ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🚀 Configura tu Examen")
    
    with st.sidebar:
        st.header("📚 Temario")
        st.write("Selecciona las clases:")
        
        # Limpieza de clases del Excel
        df_preguntas['Clase_ID'] = pd.to_numeric(df_preguntas['Clase'], errors='coerce')
        clases_num = sorted(df_preguntas['Clase_ID'].dropna().unique().astype(int))
        
        # Checkboxes dinámicos
        clases_seleccionadas = []
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("Todos"): st.session_state.clear_all = False # Lógica simple para marcar
        
        for c in clases_num:
            tema = TEMARIO.get(str(c), "Unidad de Repaso")
            if st.checkbox(f"Clase {c}: {tema}", key=f"check_{c}"):
                clases_seleccionadas.append(str(c))
    
    # Cuerpo principal
    st.markdown("### Resumen de selección")
    if not clases_seleccionadas:
        df_f = df_preguntas
        st.warning("⚠️ No has seleccionado clases específicas. Se usará **todo el banco de preguntas**.")
    else:
        df_f = df_preguntas[df_preguntas['Clase_ID'].astype(str).str.split('.').str[0].isin(clases_seleccionadas)]
        st.success(f"✅ Has seleccionado {len(clases_seleccionadas)} unidades.")
    
    st.metric("Preguntas totales disponibles", len(df_f))
    
    if st.button("🔥 COMENZAR SIMULACRO", use_container_width=True, type="primary"):
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
            st.error("La selección no tiene preguntas.")

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
    
    col_izq, col_der = st.columns([3, 1])
    with col_izq:
        st.write(f"Pregunta **{actual + 1}** de {total}")
        cid = str(pregunta['Clase']).split('.')[0]
        st.caption(f"📍 {TEMARIO.get(cid, 'Unidad ' + cid)}")
        st.progress((actual) / total)
    with col_der:
        st.markdown(f'<div class="timer-caja">⏳ {h:02d}:{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
    
    if st.button("🏁 Finalizar ahora"):
        st.session_state.finalizado = True
        st.rerun()

    st.markdown("---")
    st.markdown(f'<p class="pregunta-texto">{pregunta["Pregunta"]}</p>', unsafe_allow_html=True)
    
    opciones = [str(pregunta['Opción A']), str(pregunta['Opción B']), str(pregunta['Opción C']), str(pregunta['Opción D'])]
    correcta_val = str(pregunta['Opción Correcta']).strip()

    if not st.session_state.respondido:
        for idx, op in enumerate(opciones):
            if st.button(op, key=f"btn_{actual}_{idx}", use_container_width=True):
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
    st.title("🏁 Resultados Finales")
    total_v = st.session_state.indice_actual + (1 if st.session_state.respondido else 0)
    c1, c2, c3 = st.columns(3)
    c1.metric("Aciertos", f"{st.session_state.aciertos}")
    c2.metric("Respondidas", f"{total_v}")
    if total_v > 0:
        porcentaje = (st.session_state.aciertos/total_v)*100
        c3.metric("Efectividad", f"{porcentaje:.1f}%")
        
    if st.button("🔄 Reiniciar Simulador", use_container_width=True):
        st.session_state.examen_iniciado = False
        st.session_state.finalizado = False
        st.rerun()
