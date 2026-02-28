import streamlit as st
import pandas as pd
import random
import time

# Configuración compacta
st.set_page_config(page_title="Simulador B91", page_icon="🎓", layout="centered")

# --- TEMARIO ---
TEMARIO = {str(i): f"Unidad {i}" for i in range(1, 22)} # Simplificado para ahorro de espacio

# --- CARGA DE DATOS ---
SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
GID_USUARIOS = "1819383994"

@st.cache_data(ttl=20)
def load_all_data():
    try:
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        df_p = pd.read_csv(url_p)
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
    .pregunta-texto { font-size: 1.1rem !important; font-weight: bold; color: #1e293b; margin-bottom: 1rem; }
    .res-box { padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 2px solid #e2e8f0; }
    .res-correcta { background-color: #dcfce7 !important; border-color: #22c55e !important; color: #166534 !important; }
    .res-incorrecta { background-color: #fee2e2 !important; border-color: #ef4444 !important; color: #991b1b !important; }
    .res-neutral { background-color: #f8fafc; color: #64748b; }
    .timer-txt { font-size: 16px; font-weight: bold; color: #e11d48; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
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

# --- ESTADO ---
if 's' not in st.session_state:
    st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 't': 0, 'choice': None}

s = st.session_state.s

# --- PANTALLA INICIO ---
if not s['active'] and not s['end']:
    st.title("🎯 Bio 91")
    # Filtro inteligente por número de clase
    clases_disp = sorted(df_preguntas['Clase'].astype(str).unique())
    sel = st.multiselect("Filtrar clases:", opciones=clases_disp)
    
    if st.button("🚀 EMPEZAR", use_container_width=True, type="primary"):
        df_f = df_preguntas[df_preguntas['Clase'].astype(str).isin(sel)] if sel else df_preguntas
        if not df_f.empty:
            s['qs'] = df_f.to_dict('records')
            random.shuffle(s['qs'])
            s['qs'] = s['qs'][:60]
            s['active'] = True; s['t'] = time.time(); s['idx'] = 0; s['score'] = 0
            st.rerun()

# --- PANTALLA EXAMEN ---
elif s['active'] and not s['end']:
    q = s['qs'][s['idx']]
    quedan = 5400 - (time.time() - s['t'])
    if quedan <= 0: s['end'] = True; st.rerun()
    
    # Header compacto
    c1, c2 = st.columns([1,1])
    c1.caption(f"Pregunta {s['idx']+1}/{len(s['qs'])} • {q['Clase']}")
    c2.markdown(f'<p class="timer-txt">⏳ {int(quedan//60):02d}:{int(quedan%60):02d}</p>', unsafe_allow_html=True)

    st.markdown(f'<p class="pregunta-texto">{q["Pregunta"]}</p>', unsafe_allow_html=True)
    
    # Limpieza de opciones para comparar bien
    opts = [str(q['Opción A']).strip(), str(q['Opción B']).strip(), str(q['Opción C']).strip(), str(q['Opción D']).strip()]
    val_correcta = str(q['Opción Correcta']).strip()

    if not s['ans']:
        for i, o in enumerate(opts):
            if st.button(o, key=f"b{s['idx']}{i}", use_container_width=True):
                s['choice'] = o
                s['ans'] = True
                if s['choice'] == val_correcta: s['score'] += 1
                st.rerun()
    else:
        # AQUÍ ESTÁ EL ARREGLO: Comprobación visual forzada
        for o in opts:
            if o == val_correcta:
                # SIEMPRE pinta de verde la correcta, la hayas elegido o no
                st.markdown(f'<div class="res-box res-correcta">✅ {o}</div>', unsafe_allow_html=True)
            elif o == s['choice']:
                # Pinta de rojo solo si elegiste esta y no era la correcta
                st.markdown(f'<div class="res-box res-incorrecta">❌ {o}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="res-box res-neutral">{o}</div>', unsafe_allow_html=True)
        
        st.info(f"💡 **Explicación:** {q.get('Explicación', 'Consulta el material oficial.')}")
        
        if st.button("Siguiente ➡️", use_container_width=True, type="primary"):
            if s['idx'] + 1 < len(s['qs']):
                s['idx'] += 1; s['ans'] = False; st.rerun()
            else: s['end'] = True; st.rerun()

    st.write("---")
    if st.button("🏁 Finalizar Simulacro", type="secondary"):
        s['end'] = True; st.rerun()

# --- RESULTADOS ---
elif s['end']:
    st.title("🏁 Resultados")
    st.metric("Puntaje", f"{s['score']} / {len(s['qs'])}")
    if st.button("🔄 Reiniciar"):
        st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 't': 0, 'choice': None}
        st.rerun()
