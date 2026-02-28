import streamlit as st
import pandas as pd
import random
import time

# Configuración compacta
st.set_page_config(page_title="Simulador B91", page_icon="🎓", layout="centered")

# --- CARGA DE DATOS ---
SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
GID_USUARIOS = "1819383994"

@st.cache_data(ttl=10)
def load_all_data():
    try:
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        df_p = pd.read_csv(url_p)
        # Limpiar nombres de columnas
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
    .pregunta-texto { font-size: 1.1rem !important; font-weight: bold; color: #1e293b; margin-bottom: 1rem; }
    .res-box { padding: 12px; border-radius: 8px; margin-bottom: 8px; border: 2px solid #cbd5e1; }
    .res-correcta { background-color: #22c55e !important; color: white !important; font-weight: bold; border-color: #16a34a !important; }
    .res-incorrecta { background-color: #ef4444 !important; color: white !important; border-color: #dc2626 !important; }
    .res-neutral { background-color: #f1f5f9; color: #475569; }
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
    if df_preguntas is not None:
        clases_disp = sorted(df_preguntas['Clase'].astype(str).unique())
        sel = st.multiselect("Seleccionar Clases:", options=clases_disp)
        
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
    
    c1, c2 = st.columns([1,1])
    c1.caption(f"Pregunta {s['idx']+1}/{len(s['qs'])} • {q['Clase']}")
    c2.markdown(f'<p class="timer-txt">⏳ {int(quedan//60):02d}:{int(quedan%60):02d}</p>', unsafe_allow_html=True)

    st.markdown(f'<p class="pregunta-texto">{q["Pregunta"]}</p>', unsafe_allow_html=True)
    
    # NORMALIZACIÓN EXTREMA DE OPCIONES
    # Creamos un diccionario para mapear la opción con su texto limpio
    dicc_opts = {
        "Opción A": str(q['Opción A']).strip(),
        "Opción B": str(q['Opción B']).strip(),
        "Opción C": str(q['Opción C']).strip(),
        "Opción D": str(q['Opción D']).strip()
    }
    
    val_correcta = str(q['Opción Correcta']).strip()
    
    # Si la respuesta correcta en el Excel es "Opción A" en lugar del texto largo, lo corregimos:
    texto_correcto = dicc_opts.get(val_correcta, val_correcta)

    lista_opciones = list(dicc_opts.values())

    if not s['ans']:
        for i, o in enumerate(lista_opciones):
            if st.button(o, key=f"btn_{s['idx']}_{i}", use_container_width=True):
                s['choice'] = o
                s['ans'] = True
                if o.lower() == texto_correcto.lower():
                    s['score'] += 1
                st.rerun()
    else:
        # PINTADO MANUAL POR COMPARACIÓN
        for o in lista_opciones:
            is_correct = (o.lower() == texto_correcto.lower())
            is_user_choice = (o == s['choice'])
            
            if is_correct:
                st.markdown(f'<div class="res-box res-correcta">✅ {o}</div>', unsafe_allow_html=True)
            elif is_user_choice:
                st.markdown(f'<div class="res-box res-incorrecta">❌ {o}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="res-box res-neutral">{o}</div>', unsafe_allow_html=True)
        
        st.info(f"💡 **Explicación:** {q.get('Explicación', 'Consulta tu material de estudio.')}")
        
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
            if s['idx'] + 1 < len(s['qs']):
                s['idx'] += 1; s['ans'] = False; s['choice'] = None; st.rerun()
            else: s['end'] = True; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏁 Finalizar", type="secondary", use_container_width=True):
        s['end'] = True; st.rerun()

# --- RESULTADOS ---
elif s['end']:
    st.title("🏁 Resultados")
    st.metric("Aciertos", f"{s['score']} / {len(s['qs'])}")
    if st.button("🔄 Reiniciar"):
        st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 't': 0, 'choice': None}
        st.rerun()
