import streamlit as st
import pandas as pd
import random
import time

# Configuración inicial
st.set_page_config(page_title="Simulador Biología 91", page_icon="🎓", layout="centered")

# --- TEMARIO (Diccionario de respaldo) ---
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

@st.cache_data(ttl=15)
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
    .pregunta-texto { font-size: 19px !important; font-weight: bold; margin-bottom: 20px; color: #1f2937; }
    .opcion-resultado { padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #d1d5db; }
    .correcta { background-color: #d1fae5; color: #065f46; font-weight: bold; border: 1px solid #10b981; }
    .incorrecta { background-color: #fee2e2; color: #991b1b; border: 1px solid #ef4444; }
    .neutral { background-color: #f3f4f6; color: #4b5563; }
    .timer-caja { font-size: 22px; font-weight: bold; color: #dc2626; text-align: right; background: #fef2f2; padding: 8px; border-radius: 8px; border: 1px solid #fecaca; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE ACCESO ---
if 'acceso' not in st.session_state: st.session_state.acceso = False

if not st.session_state.acceso:
    st.title("🔐 Ingreso al Sistema")
    email = st.text_input("Email:").lower().strip()
    pin = st.text_input("PIN:", type="password").strip()
    if st.button("Entrar", use_container_width=True, type="primary"):
        if df_usuarios is not None:
            match = df_usuarios[df_usuarios['email'] == email]
            if not match.empty and str(match.iloc[0]['clave']).strip() == pin:
                st.session_state.acceso = True
                st.rerun()
            else: st.error("Credenciales no válidas.")
    st.stop()

# --- ESTADO DEL EXAMEN ---
if 'ex_iniciado' not in st.session_state:
    st.session_state.update({'ex_iniciado': False, 'fin': False, 'idx': 0, 'pts': 0, 'resp': False, 'pool': [], 't0': 0, 'sel': None})

# --- PANTALLA DE INICIO / SELECCIÓN ---
if not st.session_state.ex_iniciado and not st.session_state.fin:
    st.title("🎯 Configura tu práctica")
    
    # Generamos la lista de opciones para el selector
    opciones = [f"Clase {i}: {TEMARIO[str(i)]}" for i in range(1, 22)]
    
    st.write("### 1. Elige las clases que quieres estudiar:")
    seleccionados = st.multiselect(
        "Haz clic abajo para elegir una o varias unidades (si no eliges nada, entran todas):",
        options=opciones,
        placeholder="Ej: Clase 9, Clase 11..."
    )

    # Botón para empezar
    if st.button("🚀 EMPEZAR EXAMEN", use_container_width=True, type="primary"):
        if df_preguntas is not None:
            # Filtrar si hay selección
            if seleccionados:
                clases_ids = [s.split(":")[0].replace("Clase ", "").strip() for s in seleccionados]
                df_f = df_preguntas[df_preguntas['Clase'].astype(str).str.contains('|'.join(clases_ids))]
            else:
                df_f = df_preguntas
            
            preguntas = df_f.to_dict('records')
            random.shuffle(preguntas)
            st.session_state.pool = preguntas[:60]
            st.session_state.t0 = time.time()
            st.session_state.ex_iniciado = True
            st.rerun()

# --- PANTALLA DE EXAMEN ---
elif st.session_state.ex_iniciado and not st.session_state.fin:
    # Tiempo
    restante = 5400 - (time.time() - st.session_state.t0)
    if restante <= 0:
        st.session_state.fin = True
        st.rerun()
    
    m, s = divmod(int(restante), 60)
    h, m = divmod(m, 60)
    
    actual = st.session_state.idx
    total = len(st.session_state.pool)
    p = st.session_state.pool[actual]
    
    # Header
    c1, c2 = st.columns([2, 1])
    with c1:
        st.write(f"Pregunta {actual + 1} de {total}")
        st.caption(f"Unidad: {p['Clase']}")
    with c2:
        st.markdown(f'<p class="timer-caja">⏳ {h:02d}:{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
    
    st.progress((actual) / total)
    
    # BOTÓN PARA FINALIZAR EN CUALQUIER MOMENTO
    if st.button("🏁 Finalizar y ver nota ahora", type="secondary"):
        st.session_state.fin = True
        st.rerun()

    st.markdown("---")
    st.markdown(f'<p class="pregunta-texto">{p["Pregunta"]}</p>', unsafe_allow_html=True)
    
    ops = [str(p['Opción A']), str(p['Opción B']), str(p['Opción C']), str(p['Opción D'])]
    correcta = str(p['Opción Correcta']).strip()

    if not st.session_state.resp:
        for i, o in enumerate(ops):
            if st.button(o, key=f"b_{actual}_{i}", use_container_width=True):
                st.session_state.sel = o.strip()
                st.session_state.resp = True
                if st.session_state.sel == correcta:
                    st.session_state.pts += 1
                st.rerun()
        time.sleep(1)
        st.rerun()
    else:
        for o in ops:
            o_s = o.strip()
            if o_s == correcta: st.markdown(f'<div class="opcion-resultado correcta">✅ {o}</div>', unsafe_allow_html=True)
            elif o_s == st.session_state.sel: st.markdown(f'<div class="opcion-resultado incorrecta">❌ {o}</div>', unsafe_allow_html=True)
            else: st.markdown(f'<div class="opcion-resultado neutral">{o}</div>', unsafe_allow_html=True)
        
        st.info(f"💡 **Explicación:** {p['Explicación']}")
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
            if actual + 1 < total:
                st.session_state.idx += 1
                st.session_state.resp = False
                st.rerun()
            else:
                st.session_state.fin = True
                st.rerun()

# --- PANTALLA DE RESULTADOS ---
elif st.session_state.fin:
    st.title("🏁 Resultados")
    respondidas = st.session_state.idx + (1 if st.session_state.resp else 0)
    st.metric("Aciertos", f"{st.session_state.pts} / {respondidas}")
    
    if st.button("🔄 Reiniciar"):
        st.session_state.update({'ex_iniciado': False, 'fin': False, 'idx': 0, 'pts': 0, 'resp': False})
        st.rerun()
