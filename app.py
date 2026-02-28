import streamlit as st
import pandas as pd
import random
import time

# Configuración inicial
st.set_page_config(page_title="Simulador Premium - Biología", page_icon="🎓", layout="centered")

# --- CARGA DE DATOS ---
SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
GID_USUARIOS = "1819383994"

@st.cache_data(ttl=10)
def load_all_data():
    try:
        # URL de Preguntas (Hoja 1 - gid 0)
        url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
        df_p = pd.read_csv(url_p)
        df_p.columns = [c.strip() for c in df_p.columns]
        
        # URL de Usuarios (Hoja Usuarios)
        url_u = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_USUARIOS}"
        df_u = pd.read_csv(url_u)
        df_u.columns = [c.strip().lower() for c in df_u.columns]
        return df_p, df_u
    except Exception as e:
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
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
if 'acceso_concedido' not in st.session_state:
    st.session_state.acceso_concedido = False

if not st.session_state.acceso_concedido:
    st.title("🔒 Acceso Exclusivo - Biología")
    st.write("Ingresa tus credenciales para comenzar el simulacro.")
    
    email_user = st.text_input("Correo electrónico:").lower().strip()
    clave_user = st.text_input("Clave de acceso (PIN):", type="password").strip()
    
    if st.button("Validar Credenciales", use_container_width=True, type="primary"):
        if df_usuarios is None:
            st.error("Error al conectar con la base de datos.")
        else:
            user_match = df_usuarios[df_usuarios['email'] == email_user]
            if user_match.empty:
                st.error("El correo no se encuentra registrado.")
            else:
                clave_correcta = str(user_match.iloc[0]['clave']).strip()
                if clave_user == clave_correcta:
                    st.session_state.acceso_concedido = True
                    st.rerun()
                else:
                    st.error("La clave ingresada es incorrecta.")
    st.stop()

# --- INICIALIZACIÓN DE VARIABLES DEL EXAMEN ---
if 'examen_iniciado' not in st.session_state:
    st.session_state.update({
        'examen_iniciado': False, 
        '
