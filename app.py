import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Simulador de Examen por Temas", page_icon="🎓", layout="centered")

# --- CARGA DE DATOS ---
SHEET_ID = "1KR7OfGpqNm0aZMu3sHl2tqwRa_7AiTqENehNHjL82qM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(CSV_URL)
        # Limpieza de nombres de columnas para evitar errores de espacios
        data.columns = [c.strip() for c in data.columns]
        return data
    except:
        return None

# --- INICIALIZACIÓN ---
if 'examen_iniciado' not in st.session_state:
    st.session_state.update({
        'examen_iniciado': False,
        'finalizado': False,
        'indice_actual': 0,
        'aciertos': 0,
        'respondido': False,
        'preguntas_examen': [],
        'inicio_tiempo': 0,
        'eleccion': None
    })

df = load_data()

# --- CSS PERSONALIZADO ---
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

# --- VISTA 1: CONFIGURACIÓN E INICIO ---
if not st.session_state.examen_iniciado and not st.session_state.finalizado:
    st.title("🎓 Simulador de Examen")
    
    if df is not None:
        st.subheader("Configura tu examen")
        
        # Obtener lista de clases únicas para el selector
        lista_clases = sorted(df['Clase'].unique().tolist())
        opciones_selector = ["Todas las Clases"] + lista_clases
        
        clase_seleccionada = st.selectbox("¿Qué deseas estudiar?", opciones_selector)
        
        # Filtrar DF preliminarmente para mostrar cuántas preguntas hay
        if clase_seleccionada == "Todas las Clases":
            df_filtrado = df
        else:
            df_filtrado = df[df['Clase'] == clase_seleccionada]
            
        st.write(f"Preguntas disponibles para esta selección: **{len(df_filtrado)}**")
        
        if st.button("🚀 COMENZAR EXAMEN", use_container_width=True, type="primary"):
            # Convertir a lista de diccionarios
            pool = df_filtrado.to_dict('records')
            random.shuffle(pool)
            
            # Tomar máximo 60 o el total si hay menos
            st.session_state.preguntas_examen = pool[:60]
            st.session_state.inicio_tiempo = time.time()
            st.session_state.examen_iniciado = True
            st.session_state.indice_actual = 0
            st.session_state.aciertos = 0
            st.session_state.respondido = False
            st.rerun()
    else:
        st.error("Error al cargar el archivo de preguntas. Verifica los permisos del Excel.")

# --- VISTA 2: EXAMEN EN CURSO ---
elif st.session_state.examen_iniciado and not st.session_state.finalizado:
    # Lógica del reloj
    tiempo_total = 5400 # 90 minutos
    transcurrido = time.time() - st.session_state.inicio_tiempo
    restante = tiempo_total - transcurrido

    if restante <= 0:
        st.session_state.finalizado = True
        st.rerun()

    m, s = divmod(int(restante), 60)
    h, m = divmod(m, 60)
    
    actual = st.session_state.indice_actual
    total = len(st.session_state.preguntas_examen)
    pregunta = st.session_state.preguntas_examen[actual]
    
    # Header
    c1, c2 = st.columns([2, 1])
    with c1: 
        st.write(f"Pregunta {actual + 1} de {total}")
        st.caption(f"Clase: {pregunta['Clase']} | Tema: {pregunta['Tema']}")
    with c2: 
        st.markdown(f'<p class="timer-caja">⏳ {h:02d}:{m:02d}:{s:02d}</p>', unsafe_allow_html=True)
    
    st.progress(actual / total)

    # Mostrar Pregunta (Nuevos nombres de columnas)
    st.markdown(f'<p class="pregunta-texto">{pregunta["Pregunta"]}</p>', unsafe_allow_html=True)
    
    # Mapeo de opciones según tu nuevo formato
    opciones = [
        str(pregunta['Opción A']), 
        str(pregunta['Opción B']), 
        str(pregunta['Opción C']), 
        str(pregunta['Opción D'])
    ]
    correcta_val = str(pregunta['Opción Correcta']).strip()

    if not st.session_state.respondido:
        for idx, op in enumerate(opciones):
            if st.button(op, key=f"btn_{actual}_{idx}", use_container_width=True):
                st.session_state.eleccion = op.strip()
                st.session_state.respondido = True
                if st.session_state.eleccion == correcta_val:
                    st.session_state.aciertos += 1
                st.rerun()
        
        # Reloj en tiempo real (solo refresca mientras no se ha respondido)
        time.sleep(1)
        st.rerun()
        
    else:
        # Colores de respuesta
        for op in opciones:
            op_s = op.strip()
            if op_s == correcta_val:
                st.markdown(f'<div class="opcion-resultado correcta">✅ {op}</div>', unsafe_allow_html=True)
            elif op_s == st.session_state.eleccion:
                st.markdown(f'<div class="opcion-resultado incorrecta">❌ {op}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="opcion-resultado neutral">{op}</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div style="font-size:18px; background-color:#e9f5ff; padding:15px; border-radius:10px; border-left:5px solid #17a2b8; margin-top:15px;">'
                    f'<b>💡 Explicación:</b><br>{pregunta["Explicación"]}</div>', unsafe_allow_html=True)
        
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
            if actual + 1 < total:
                st.session_state.indice_actual += 1
                st.session_state.respondido = False
                st.rerun()
            else:
                st.session_state.finalizado = True
                st.rerun()

# --- VISTA 3: RESULTADOS ---
elif st.session_state.finalizado:
    st.title("🏁 Examen Finalizado")
    total_q = len(st.session_state.preguntas_examen)
    st.metric("Resultado", f"{st.session_state.aciertos} / {total_q} aciertos")
    
    nota = (st.session_state.aciertos / total_q) * 10 if total_q > 0 else 0
    if nota >= 6:
        st.success(f"¡Buen trabajo! Tu nota es: {nota:.1f}/10")
    else:
        st.warning(f"Sigue practicando. Tu nota es: {nota:.1f}/10")
        
    if st.button("🔄 Volver al Inicio"):
        st.session_state.examen_iniciado = False
        st.session_state.finalizado = False
        st.rerun()
