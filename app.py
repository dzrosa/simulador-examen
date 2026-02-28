import streamlit as st
import pandas as pd
import random
import time

# Configuración de página
st.set_page_config(page_title="Biología CBC 2026", page_icon="🎓", layout="centered")

# --- DICCIONARIO DE TEMAS (Para mostrar en el selector) ---
TEMARIO_DETALLADO = {
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

@st.cache_data(ttl=60)
def load_all_data():
    try:
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        df_p = pd.read_csv(url_p)
        df_p.columns = [c.strip() for c in df_p.columns]
        url_u = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_USUARIOS}"
        df_u = pd.read_csv(url_u)
        df_u.columns = [c.strip().lower() for c in df_u.columns]
        return df_p, df_u
    except: return None, None

df_preguntas, df_usuarios = load_all_data()

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; }
    .pregunta-texto { font-size: 1.2rem !important; font-weight: bold; color: #1e293b; margin-bottom: 1.5rem; line-height: 1.4; }
    .res-box { padding: 14px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #cbd5e1; font-size: 1rem; }
    .res-correcta { background-color: #22c55e !important; color: white !important; font-weight: bold; border-color: #16a34a !important; }
    .res-incorrecta { background-color: #ef4444 !important; color: white !important; border-color: #dc2626 !important; }
    .res-neutral { background-color: #f8fafc; color: #334155; }
    hr { margin: 2rem 0; }
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
            else: st.error("Credenciales incorrectas")
    st.stop()

# --- ESTADO ---
if 's' not in st.session_state:
    st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}

s = st.session_state.s

# --- VISTA 1: INICIO ---
if not s['active'] and not s['end']:
    st.title("🎓 Biología CBC Verano 2026")
    st.subheader("Selecciona los temas para practicar")
    
    opcion_todos = st.checkbox("✅ Practicar con TODOS LOS TEMAS")
    
    # Creamos la lista de opciones: "Clase 1: Tema..."
    opciones_format = [f"Clase {k}: {v}" for k, v in TEMARIO_DETALLADO.items()]
    
    sel = []
    if not opcion_todos:
        sel = st.multiselect("Elegir temas:", options=opciones_format, placeholder="Haz clic para buscar unidades...")
    
    if st.button("🚀 EMPEZAR EXAMEN", use_container_width=True, type="primary"):
        if df_preguntas is not None:
            if opcion_todos:
                df_f = df_preguntas
            elif sel:
                # Extraemos solo el número de clase de lo seleccionado
                numeros_clase = [item.split(":")[0].replace("Clase ", "").strip() for item in sel]
                # Filtro robusto: buscamos el número dentro de la columna Clase del Excel
                df_f = df_preguntas[df_preguntas['Clase'].astype(str).apply(lambda x: any(num in "".join(filter(str.isdigit, x)) for num in numeros_clase))]
            else:
                df_f = pd.DataFrame()

            if not df_f.empty:
                s['qs'] = df_f.to_dict('records')
                random.shuffle(s['qs'])
                s['qs'] = s['qs'][:60]
                s['active'] = True
                s['idx'] = 0
                s['score'] = 0
                s['ans'] = False
                st.rerun()
            else:
                st.warning("Selecciona al menos una unidad para comenzar.")

# --- VISTA 2: EXAMEN ---
elif s['active'] and not s['end']:
    q = s['qs'][s['idx']]
    
    # Indicador de progreso simple
    st.caption(f"Pregunta {s['idx']+1} de {len(s['qs'])} • {q['Clase']}")
    st.markdown(f'<p class="pregunta-texto">{q["Pregunta"]}</p>', unsafe_allow_html=True)
    
    # Mapeo de opciones
    opts_dict = {
        "A": str(q['Opción A']).strip(),
        "B": str(q['Opción B']).strip(),
        "C": str(q['Opción C']).strip(),
        "D": str(q['Opción D']).strip()
    }
    
    correcta_raw = str(q['Opción Correcta']).strip()
    # Si el Excel dice "Opción A" o solo "A", lo convertimos al texto real
    key_map = {"Opción A": "A", "Opción B": "B", "Opción C": "C", "Opción D": "D"}
    key_clean = key_map.get(correcta_raw, correcta_raw)
    texto_correcto = opts_dict.get(key_clean, correcta_raw)
    
    lista_opciones = list(opts_dict.values())

    if not s['ans']:
        for i, opt in enumerate(lista_opciones):
            if st.button(opt, key=f"btn_{s['idx']}_{i}", use_container_width=True):
                s['choice'] = opt.strip()
                s['ans'] = True
                if s['choice'].lower() == texto_correcto.lower():
                    s['score'] += 1
                st.rerun()
    else:
        # FEEDBACK VISUAL
        for opt in lista_opciones:
            opt_clean = opt.strip()
            es_correcta = (opt_clean.lower() == texto_correcto.lower())
            es_elegida = (opt_clean == s['choice'])
            
            if es_correcta:
                st.markdown(f'<div class="res-box res-correcta">✅ {opt}</div>', unsafe_allow_html=True)
            elif es_elegida:
                st.markdown(f'<div class="res-box res-incorrecta">❌ {opt}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="res-box res-neutral">{opt}</div>', unsafe_allow_html=True)
        
        st.info(f"💡 **Explicación:** {q.get('Explicación', 'Consulta el material oficial de la cátedra para profundizar.')}")
        
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
            if s['idx'] + 1 < len(s['qs']):
                s['idx'] += 1
                s['ans'] = False
                s['choice'] = None
                st.rerun()
            else:
                s['end'] = True
                st.rerun()

    st.markdown("<br><hr>", unsafe_allow_html=True)
    if st.button("🏁 Finalizar y ver resultados", type="secondary", use_container_width=True):
        s['end'] = True
        st.rerun()

# --- VISTA 3: RESULTADOS ---
elif s['end']:
    st.title("🏁 Resultados Finales")
    c1, c2 = st.columns(2)
    c1.metric("Aciertos", f"{s['score']} / {len(s['qs'])}")
    porcentaje = (s['score']/len(s['qs'])*100) if s['qs'] else 0
    c2.metric("Efectividad", f"{porcentaje:.1f}%")
    
    if st.button("🔄 Nueva práctica", use_container_width=True):
        st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}
        st.rerun()
