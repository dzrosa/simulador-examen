import streamlit as st
import pandas as pd
import random
import time

# Configuración inicial
st.set_page_config(page_title="Simulador Biología 91", page_icon="🎓", layout="centered")

# --- TEMARIO ---
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

@st.cache_data(ttl=30)
def load_all_data():
    try:
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        df_p = pd.read_csv(url_p)
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
    .pregunta-texto { font-size: 20px !important; font-weight: bold; margin-bottom: 25px; color: #1e293b; }
    .res-box { padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #e2e8f0; font-size: 16px; }
    .res-correcta { background-color: #dcfce7 !important; border-color: #22c55e !important; color: #166534 !important; font-weight: bold; }
    .res-incorrecta { background-color: #fee2e2 !important; border-color: #ef4444 !important; color: #991b1b !important; }
    .res-neutral { background-color: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
    .timer { font-size: 24px; font-weight: bold; color: #e11d48; background: #fff1f2; padding: 10px; border-radius: 8px; border: 1px solid #fda4af; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE ACCESO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso")
    u = st.text_input("Email:").lower().strip()
    p = st.text_input("PIN:", type="password").strip()
    if st.button("Entrar", use_container_width=True):
        if df_usuarios is not None:
            match = df_usuarios[df_usuarios['email'] == u]
            if not match.empty and str(match.iloc[0]['clave']).strip() == p:
                st.session_state.auth = True
                st.rerun()
            else: st.error("Error de credenciales")
    st.stop()

# --- ESTADO DEL SIMULADOR ---
if 'state' not in st.session_state:
    st.session_state.state = {'started': False, 'over': False, 'idx': 0, 'score': 0, 'answered': False, 'questions': [], 'time': 0, 'user_choice': None}

s = st.session_state.state

# --- VISTA 1: SELECCIÓN ---
if not s['started'] and not s['over']:
    st.title("🎯 Practicar por Unidad")
    
    lista_temas = [f"Clase {i}: {TEMARIO[str(i)]}" for i in range(1, 22)]
    seleccion = st.multiselect("Selecciona una o varias unidades (si dejas vacío, entran todas):", options=lista_temas)

    if st.button("🚀 INICIAR EXAMEN", use_container_width=True, type="primary"):
        if df_preguntas is not None:
            df_working = df_preguntas.copy()
            # Limpiamos la columna Clase del Excel para que sea numérica
            df_working['Clase_Num'] = pd.to_numeric(df_working['Clase'], errors='coerce').fillna(0).astype(int)
            
            if seleccion:
                clases_ids = [int(sel.split(":")[0].replace("Clase ", "").strip()) for sel in seleccion]
                df_f = df_working[df_working['Clase_Num'].isin(clases_ids)]
            else:
                df_f = df_working
            
            if len(df_f) == 0:
                st.error("❌ No se encontraron preguntas para las clases seleccionadas. Revisa la columna 'Clase' en tu Excel.")
            else:
                lista_p = df_f.to_dict('records')
                random.shuffle(lista_p)
                s['questions'] = lista_p[:60]
                s['time'] = time.time()
                s['started'] = True
                s['idx'] = 0
                s['score'] = 0
                st.rerun()

# --- VISTA 2: EXAMEN ---
elif s['started'] and not s['over']:
    # Seguridad: Si por algún motivo la lista está vacía, resetear
    if not s['questions']:
        s['started'] = False
        st.rerun()

    quedan = 5400 - (time.time() - s['time'])
    if quedan <= 0: s['over'] = True; st.rerun()
    
    m, sec = divmod(int(quedan), 60)
    h, m = divmod(m, 60)
    
    q = s['questions'][s['idx']]
    
    c1, c2 = st.columns([3, 1])
    with c1:
        st.write(f"Pregunta {s['idx'] + 1} de {len(s['questions'])}")
        st.caption(f"Unidad {q.get('Clase', '?')}")
        st.progress((s['idx']) / len(s['questions']))
    with c2:
        st.markdown(f'<div class="timer">⏳ {h:02d}:{m:02d}:{sec:02d}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<p class="pregunta-texto">{q["Pregunta"]}</p>', unsafe_allow_html=True)
    
    opciones = [str(q['Opción A']), str(q['Opción B']), str(q['Opción C']), str(q['Opción D'])]
    correcta = str(q['Opción Correcta']).strip()

    if not s['answered']:
        for i, opt in enumerate(opciones):
            if st.button(opt, key=f"opt_{s['idx']}_{i}", use_container_width=True):
                s['user_choice'] = opt.strip()
                s['answered'] = True
                if s['user_choice'] == correcta:
                    s['score'] += 1
                st.rerun()
    else:
        for opt in opciones:
            opt_s = opt.strip()
            if opt_s == correcta:
                st.markdown(f'<div class="res-box res-correcta">✅ {opt}</div>', unsafe_allow_html=True)
            elif opt_s == s['user_choice']:
                st.markdown(f'<div class="res-box res-incorrecta">❌ {opt}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="res-box res-neutral">{opt}</div>', unsafe_allow_html=True)
        
        st.info(f"💡 **Explicación:** {q.get('Explicación', 'Revisa el material de la Clase ' + str(q.get('Clase')))}")
        
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
            if s['idx'] + 1 < len(s['questions']):
                s['idx'] += 1
                s['answered'] = False
                st.rerun()
            else:
                s['over'] = True
                st.rerun()

# --- VISTA 3: RESULTADOS ---
elif s['over']:
    st.title("🏁 Resultados")
    st.metric("Puntaje Total", f"{s['score']} / {len(s['questions'])}")
    if st.button("🔄 Volver al Inicio"):
        st.session_state.state = {'started': False, 'over': False, 'idx': 0, 'score': 0, 'answered': False, 'questions': [], 'time': 0, 'user_choice': None}
        st.rerun()
