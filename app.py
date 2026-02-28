import streamlit as st
import pandas as pd
import random
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Biología CBC 2026", page_icon="🎓", layout="centered")

SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
GID_USUARIOS = "1819383994"

# Diccionario de temas para el selector (Personalizado)
TEMARIO_DETALLE = {
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

# 2. CARGA DE DATOS DESDE EXCEL
@st.cache_data(ttl=60)
def cargar_datos():
    try:
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        df = pd.read_csv(url_p)
        # Limpiamos nombres de columnas para evitar el KeyError
        df.columns = [c.strip() for c in df.columns]
        
        url_u = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_USUARIOS}"
        df_u = pd.read_csv(url_u)
        df_u.columns = [c.strip().lower() for c in df_u.columns]
        return df, df_u
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None

df_preguntas, df_usuarios = cargar_datos()

# 3. ESTILOS
st.markdown("""
    <style>
    .pregunta-texto { font-size: 1.2rem; font-weight: bold; color: #1e293b; margin-bottom: 1.5rem; }
    .res-box { padding: 14px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #cbd5e1; }
    .res-correcta { background-color: #22c55e !important; color: white !important; font-weight: bold; border-color: #16a34a !important; }
    .res-incorrecta { background-color: #ef4444 !important; color: white !important; border-color: #dc2626 !important; }
    .res-neutral { background-color: #f8fafc; color: #334155; }
    .aprobado { color: #22c55e; font-size: 24px; font-weight: bold; text-align: center; }
    .reprobado { color: #ef4444; font-size: 24px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 4. LOGIN
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso")
    u = st.text_input("Email:").lower().strip()
    p = st.text_input("PIN:", type="password").strip()
    if st.button("Entrar"):
        if df_usuarios is not None:
            match = df_usuarios[df_usuarios['email'] == u]
            if not match.empty and str(match.iloc[0]['clave']).strip() == p:
                st.session_state.auth = True; st.rerun()
    st.stop()

# 5. ESTADO DE LA APP
if 's' not in st.session_state:
    st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}

s = st.session_state.s

# --- VISTA INICIO ---
if not s['active'] and not s['end']:
    st.title("🎓 Biología CBC Verano 2026")
    st.subheader("Configura tu examen")
    
    todas = st.checkbox("✅ Practicar con TODOS LOS TEMAS")
    opciones_selector = [f"Clase {k}: {v}" for k, v in TEMARIO_DETALLE.items()]
    
    sel = []
    if not todas:
        sel = st.multiselect("Elegir temas:", options=opciones_selector, placeholder="Selecciona unidades")
    
    if st.button("🚀 EMPEZAR", use_container_width=True, type="primary"):
        if todas:
            pool_df = df_preguntas
        else:
            nums = [item.split(":")[0].replace("Clase ", "").strip() for item in sel]
            pool_df = df_preguntas[df_preguntas['Clase'].astype(str).isin(nums)]
        
        if not pool_df.empty:
            # Convertimos el Excel a una lista de diccionarios para mezclar
            pool = pool_df.to_dict('records')
            random.shuffle(pool)
            
            # PREPARACIÓN DE CADA PREGUNTA (MEZCLA DE OPCIONES)
            for p in pool:
                # Identificamos la correcta basándonos en lo que dice la columna 'Opción Correcta'
                # (Ya sea que diga el texto o diga 'Opción A', etc.)
                mapa_letras = {"Opción A": p['Opción A'], "Opción B": p['Opción B'], "Opción C": p['Opción C'], "Opción D": p['Opción D']}
                p['final_correcta'] = mapa_letras.get(p['Opción Correcta'], p['Opción Correcta'])
                
                # Armamos la lista de opciones y la mezclamos
                opts = [p['Opción A'], p['Opción B'], p['Opción C'], p['Opción D']]
                random.shuffle(opts)
                p['lista_mezclada'] = opts
            
            s['qs'] = pool[:60] # Máximo 60
            s['active'] = True; s['idx'] = 0; s['score'] = 0; s['ans'] = False
            st.rerun()

# --- VISTA EXAMEN ---
elif s['active'] and not s['end']:
    q = s['qs'][s['idx']]
    st.caption(f"Pregunta {s['idx']+1} de {len(s['qs'])} • Clase {q['Clase']}")
    st.markdown(f'<p class="pregunta-texto">{q["Pregunta"]}</p>', unsafe_allow_html=True)

    if not s['ans']:
        for i, opt in enumerate(q['lista_mezclada']):
            if st.button(opt, key=f"b_{s['idx']}_{i}", use_container_width=True):
                s['choice'] = opt
                s['ans'] = True
                if str(s['choice']).strip() == str(q['final_correcta']).strip():
                    s['score'] += 1
                st.rerun()
    else:
        for opt in q['lista_mezclada']:
            if str(opt).strip() == str(q['final_correcta']).strip():
                st.markdown(f'<div class="res-box res-correcta">✅ {opt}</div>', unsafe_allow_html=True)
            elif opt == s['choice']:
                st.markdown(f'<div class="res-box res-incorrecta">❌ {opt}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="res-box res-neutral">{opt}</div>', unsafe_allow_html=True)
        
        st.info(f"💡 **Explicación:** {q.get('Explicación', 'Sin explicación disponible.')}")
        
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
            if s['idx'] + 1 < len(s['qs']):
                s['idx'] += 1; s['ans'] = False; s['choice'] = None; st.rerun()
            else: s['end'] = True; st.rerun()

# --- VISTA RESULTADOS ---
elif s['end']:
    st.title("🏁 Resultados")
    score = s['score']
    total = len(s['qs'])
    st.metric("Puntaje", f"{score} / {total}")
    
    if score >= 36:
        st.markdown('<p class="aprobado">¡APROBADO! 🎉</p>', unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f'<p class="reprobado">No alcanzaste el mínimo (36/{total}). <br> ¡A seguir estudiando!</p>', unsafe_allow_html=True)
    
    if st.button("🔄 Reiniciar"):
        st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}
        st.rerun()
