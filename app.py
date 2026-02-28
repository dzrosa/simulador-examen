import streamlit as st
import pandas as pd
import random
import time

# Configuración de página
st.set_page_config(page_title="Biología CBC 2026", page_icon="🎓", layout="centered")

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
    .main .block-container { padding-top: 1rem; }
    .pregunta-texto { font-size: 1.15rem !important; font-weight: bold; color: #1e293b; margin-bottom: 1.2rem; }
    .res-box { padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 2px solid #cbd5e1; }
    .res-correcta { background-color: #22c55e !important; color: white !important; font-weight: bold; border-color: #16a34a !important; }
    .res-incorrecta { background-color: #ef4444 !important; color: white !important; border-color: #dc2626 !important; }
    .res-neutral { background-color: #f1f5f9; color: #475569; }
    .timer-txt { font-size: 18px; font-weight: bold; color: #e11d48; text-align: right; }
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
            else: st.error("PIN o Email incorrecto")
    st.stop()

# --- ESTADO DEL SISTEMA ---
if 's' not in st.session_state:
    st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 't_inicio': 0, 'choice': None}

s = st.session_state.s

# --- PANTALLA INICIO ---
if not s['active'] and not s['end']:
    st.title("🎓 Biología CBC Verano 2026")
    
    if df_preguntas is not None:
        # Extraer y ordenar clases numéricamente
        clases_raw = df_preguntas['Clase'].astype(str).unique()
        # Intentamos ordenar de forma inteligente (numérica)
        try:
            clases_ordenadas = sorted(clases_raw, key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))
        except:
            clases_ordenadas = sorted(clases_raw)

        st.subheader("Configura tu práctica")
        opcion_todos = st.checkbox("Seleccionar TODOS LOS TEMAS")
        
        sel = []
        if not opcion_todos:
            sel = st.multiselect("Elegir temas:", options=clases_ordenadas, placeholder="Selecciona una o varias clases")
        
        if st.button("🚀 EMPEZAR SIMULACRO", use_container_width=True, type="primary"):
            if opcion_todos:
                df_f = df_preguntas
            else:
                df_f = df_preguntas[df_preguntas['Clase'].astype(str).isin(sel)] if sel else df_preguntas
            
            if not df_f.empty:
                s['qs'] = df_f.to_dict('records')
                random.shuffle(s['qs'])
                s['qs'] = s['qs'][:60] # Límite de 60 preguntas
                s['active'] = True
                s['t_inicio'] = time.time()
                s['idx'] = 0
                s['score'] = 0
                s['ans'] = False
                st.rerun()
            else:
                st.warning("Por favor, selecciona al menos una clase o marca 'Todos los temas'.")

# --- PANTALLA EXAMEN ---
elif s['active'] and not s['end']:
    q = s['qs'][s['idx']]
    
    # RELOJ EN VIVO
    t_actual = time.time()
    transcurrido = t_actual - s['t_inicio']
    quedan = 5400 - transcurrido # 90 minutos
    
    if quedan <= 0: 
        s['end'] = True
        st.rerun()
    
    # Header Compacto
    c1, c2 = st.columns([2, 1])
    with c1:
        st.caption(f"Pregunta {s['idx']+1} de {len(s['qs'])} • {q['Clase']}")
    with c2:
        m, seg = divmod(int(quedan), 60)
        st.markdown(f'<p class="timer-txt">⏳ {m:02d}:{seg:02d}</p>', unsafe_allow_html=True)

    st.markdown(f'<p class="pregunta-texto">{q["Pregunta"]}</p>', unsafe_allow_html=True)
    
    # Preparar opciones y respuesta correcta con limpieza total
    opts_map = {
        "Opción A": str(q['Opción A']).strip(),
        "Opción B": str(q['Opción B']).strip(),
        "Opción C": str(q['Opción C']).strip(),
        "Opción D": str(q['Opción D']).strip()
    }
    
    val_correcta_raw = str(q['Opción Correcta']).strip()
    # Si el excel dice "Opción A", buscamos el texto. Si ya es el texto, lo dejamos.
    texto_correcto = opts_map.get(val_correcta_raw, val_correcta_raw)
    
    lista_desordenada = list(opts_map.values())

    if not s['ans']:
        for i, o in enumerate(lista_desordenada):
            if st.button(o, key=f"btn_{s['idx']}_{i}", use_container_width=True):
                s['choice'] = o.strip()
                s['ans'] = True
                # Comparación robusta
                if s['choice'].lower() == texto_correcto.lower():
                    s['score'] += 1
                st.rerun()
    else:
        # MOSTRAR RESULTADOS (VERDE Y ROJO)
        for o in lista_desordenada:
            o_clean = o.strip()
            es_correcta = (o_clean.lower() == texto_correcto.lower())
            es_elegida = (o_clean == s['choice'])
            
            if es_correcta:
                st.markdown(f'<div class="res-box res-correcta">✅ {o}</div>', unsafe_allow_html=True)
            elif es_elegida:
                st.markdown(f'<div class="res-box res-incorrecta">❌ {o}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="res-box res-neutral">{o}</div>', unsafe_allow_html=True)
        
        st.info(f"💡 **Explicación:** {q.get('Explicación', 'Consulta el material de estudio de esta unidad.')}")
        
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
            if s['idx'] + 1 < len(s['qs']):
                s['idx'] += 1
                s['ans'] = False
                s['choice'] = None
                st.rerun()
            else:
                s['end'] = True
                st.rerun()

    # Botón Finalizar al pie
    st.markdown("<br><hr>", unsafe_allow_html=True)
    if st.button("🏁 Finalizar y ver puntaje", type="secondary", use_container_width=True):
        s['end'] = True
        st.rerun()

# --- PANTALLA RESULTADOS ---
elif s['end']:
    st.title("🏁 Resultados Finales")
    c1, c2 = st.columns(2)
    c1.metric("Puntaje", f"{s['score']} / {len(s['qs'])}")
    efectividad = (s['score']/len(s['qs'])*100) if s['qs'] else 0
    c2.metric("Efectividad", f"{efectividad:.1f}%")
    
    if st.button("🔄 Volver a practicar", use_container_width=True):
        st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 't_inicio': 0, 'choice': None}
        st.rerun()
