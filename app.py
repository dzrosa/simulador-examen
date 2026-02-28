import streamlit as st
import pandas as pd
import random

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Biología CBC 2026", page_icon="🎓", layout="centered")

SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
GID_USUARIOS = "1819383994"

# Diccionario maestro de temas
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

@st.cache_data(ttl=60)
def cargar_datos():
    try:
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        df = pd.read_csv(url_p)
        df.columns = [c.strip() for c in df.columns]
        
        url_u = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_USUARIOS}"
        df_u = pd.read_csv(url_u)
        df_u.columns = [c.strip().lower() for c in df_u.columns]
        return df, df_u
    except:
        return None, None

df_preguntas, df_usuarios = cargar_datos()

# 3. ESTILOS CSS (CORRECCIÓN TOTAL DE CONTRASTE E INPUTS)
st.markdown("""
    <style>
    /* 1. Fondo general blanco y texto oscuro */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: white !important;
        color: #1e293b !important;
    }

    /* 2. Forzar color en todos los textos */
    .stMarkdown, p, span, label, .stCaption, h1, h2, h3, .stSelectbox label {
        color: #1e293b !important;
    }

    /* 3. INPUTS Y SELECTORES (Fondo blanco, texto negro) */
    input[type="text"], input[type="password"], [data-baseweb="select"], [data-baseweb="popover"] {
        background-color: white !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    /* Corregir el texto dentro de los campos de texto al escribir */
    input {
        color: #1e293b !important;
        -webkit-text-fill-color: #1e293b !important;
    }

    /* 4. BOTÓN CTA (Primario: Azul con texto Blanco) */
    .stButton>button[kind="primary"] {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        box-shadow: none !important;
    }
    
    /* Forzar el color blanco del texto del botón primario incluso al pasar el mouse */
    .stButton>button[kind="primary"]:hover, .stButton>button[kind="primary"]:active, .stButton>button[kind="primary"]:focus {
        color: white !important;
        background-color: #1d4ed8 !important;
    }

    /* 5. BOTONES NORMALES (Opciones de respuesta) */
    .stButton>button {
        color: #1e293b !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* 6. CAJAS DE RESPUESTA (Feedback) */
    .res-box { 
        padding: 14px; border-radius: 10px; margin-bottom: 10px; 
        border: 2px solid #cbd5e1; color: #1e293b !important; 
    }
    .res-correcta { background-color: #22c55e !important; color: white !important; }
    .res-incorrecta { background-color: #ef4444 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Acceso")
    u = st.text_input("Email:").lower().strip()
    p = st.text_input("PIN:", type="password").strip()
    if st.button("Entrar", use_container_width=True):
        if df_usuarios is not None:
            match = df_usuarios[df_usuarios['email'] == u]
            if not match.empty and str(match.iloc[0]['clave']).strip() == p:
                st.session_state.auth = True; st.rerun()
    st.stop()

if 's' not in st.session_state:
    st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}

s = st.session_state.s

# --- PANTALLA INICIO ---
if not s['active'] and not s['end']:
    st.title("🎓 Biología CBC Verano 2026")
    todas = st.checkbox("✅ Practicar con TODOS LOS TEMAS")
    
    opciones_selector = [f"Clase {k}: {v}" for k, v in TEMARIO_DETALLE.items()]
    sel = [] if todas else st.multiselect("Elegir temas:", options=opciones_selector)
    
    if st.button("🚀 EMPEZAR", use_container_width=True, type="primary"):
        if todas:
            pool_df = df_preguntas
        else:
            # LÓGICA DE FILTRADO FLEXIBLE
            nums_elegidos = [item.split(":")[0].replace("Clase ", "").strip() for item in sel]
            # Buscamos si el número de clase está contenido en el texto de la columna 'Clase'
            pool_df = df_preguntas[df_preguntas['Clase'].astype(str).apply(lambda x: any(n == "".join(filter(str.isdigit, x)) for n in nums_elegidos))]
        
        if not pool_df.empty:
            pool = pool_df.to_dict('records')
            random.shuffle(pool)
            for p in pool:
                # Mapeo de la correcta
                mapa = {"Opción A": p['Opción A'], "Opción B": p['Opción B'], "Opción C": p['Opción C'], "Opción D": p['Opción D']}
                p['final_correcta'] = mapa.get(p['Opción Correcta'], p['Opción Correcta'])
                # Mezclamos opciones
                opts = [str(p['Opción A']), str(p['Opción B']), str(p['Opción C']), str(p['Opción D'])]
                random.shuffle(opts)
                p['lista_mezclada'] = opts
            
            s['qs'] = pool[:60]
            s['active'] = True; s['idx'] = 0; s['score'] = 0; s['ans'] = False
            st.rerun()
        else:
            st.error(f"No se encontraron preguntas. Verifica que en el Excel la columna 'Clase' tenga los números: {', '.join(nums_elegidos)}")

# --- PANTALLA EXAMEN ---
elif s['active'] and not s['end']:
    q = s['qs'][s['idx']]
    
    # Quitamos el prefijo "Clase" manual para evitar el "Clase Clase"
    clase_label = str(q['Clase'])
    st.caption(f"Pregunta {s['idx']+1} de {len(s['qs'])} • {clase_label}")
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
        
        st.info(f"💡 **Explicación:** {q.get('Explicación', 'Consulta el material de clase.')}")
        
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
            if s['idx'] + 1 < len(s['qs']):
                s['idx'] += 1; s['ans'] = False; s['choice'] = None; st.rerun()
            else: s['end'] = True; st.rerun()

    st.write("---")
    if st.button("🏁 Finalizar Examen", use_container_width=True):
        s['end'] = True; st.rerun()

# --- PANTALLA RESULTADOS ---
elif s['end']:
    st.title("🏁 Resultados")
    score, total = s['score'], len(s['qs'])
    st.metric("Puntaje", f"{score} / {total}")
    if score >= 36:
        st.success("¡APROBADO! 🎉")
        st.balloons()
    else:
        st.error(f"Puntaje: {score} (Necesitas 36 para aprobar).")
    
    if st.button("🔄 Reiniciar", use_container_width=True):
        st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}
        st.rerun()


