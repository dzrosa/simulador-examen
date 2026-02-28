import streamlit as st
import random

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Biología CBC 2026", page_icon="🎓", layout="centered")

# 2. BASE DE DATOS DE PREGUNTAS (HARDCODED)
# Aquí puedes ir pegando tus preguntas. 
# REGLA: La primera opción de la lista DEBE ser la correcta. El código las mezclará.
def obtener_preguntas_db():
    return [
        {
            "nro_clase": "1",
            "tema": "Características de los seres vivos",
            "pregunta": "¿Cuál es la unidad estructural y funcional de todos los seres vivos?",
            "opciones": ["La célula", "El átomo", "La molécula", "El tejido"],
            "explicacion": "Según la Teoría Celular, la célula es la unidad mínima de vida."
        },
        {
            "nro_clase": "1",
            "tema": "Características de los seres vivos",
            "pregunta": "La capacidad de mantener el equilibrio interno frente a cambios externos se denomina:",
            "opciones": ["Homeostasis", "Metabolismo", "Irritabilidad", "Evolución"],
            "explicacion": "La homeostasis permite regular condiciones como pH o temperatura."
        },
        {
            "nro_clase": "2",
            "tema": "Agua y pH",
            "pregunta": "¿Qué tipo de unión química mantiene unidas a las moléculas de agua entre sí?",
            "opciones": ["Puentes de hidrógeno", "Unión covalente", "Unión iónica", "Fuerzas de Van der Waals"],
            "explicacion": "La polaridad del agua permite la formación de puentes de hidrógeno entre el O y el H de moléculas vecinas."
        }
    ]

# 3. TEMARIO (Para el selector de unidades)
TEMARIO = {
    "1": "Características de los seres vivos y Teoría celular",
    "2": "Estructura atómica, Agua y pH",
    "3": "Biomoléculas: Glúcidos, Lípidos y Ácidos Nucleicos",
    # Agrega aquí los demás según necesites
}

# 4. ESTILOS CSS
st.markdown("""
    <style>
    .pregunta-texto { font-size: 1.2rem !important; font-weight: bold; color: #1e293b; margin-bottom: 1.5rem; }
    .res-box { padding: 14px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #cbd5e1; }
    .res-correcta { background-color: #22c55e !important; color: white !important; font-weight: bold; border-color: #16a34a !important; }
    .res-incorrecta { background-color: #ef4444 !important; color: white !important; border-color: #dc2626 !important; }
    .res-neutral { background-color: #f8fafc; color: #334155; }
    </style>
    """, unsafe_allow_html=True)

# 5. INICIALIZACIÓN DE ESTADO
if 's' not in st.session_state:
    st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}

s = st.session_state.s

# --- PANTALLA INICIO ---
if not s['active'] and not s['end']:
    st.title("🎓 Biología CBC Verano 2026")
    st.subheader("Configura tu práctica")
    
    todas = st.checkbox("Practicar con TODOS LOS TEMAS")
    opciones_menu = [f"Clase {k}: {v}" for k, v in TEMARIO.items()]
    
    sel = []
    if not todas:
        sel = st.multiselect("Elegir temas:", options=opciones_menu, placeholder="Selecciona una o varias unidades")
    
    if st.button("🚀 EMPEZAR EXAMEN", use_container_width=True, type="primary"):
        db = obtener_preguntas_db()
        
        if todas:
            pool = db
        else:
            numeros_elegidos = [item.split(":")[0].replace("Clase ", "").strip() for item in sel]
            pool = [p for p in db if p['nro_clase'] in numeros_elegidos]

        if pool:
            # PROCESO DE MEZCLADO
            random.shuffle(pool) # Mezcla el orden de las preguntas
            for p in pool:
                p['correcta'] = p['opciones'][0] # Guardamos la correcta (siempre la primera en la DB)
                random.shuffle(p['opciones'])   # Mezclamos las opciones para el alumno
            
            s['qs'] = pool[:60]
            s['active'] = True; s['idx'] = 0; s['score'] = 0; s['ans'] = False
            st.rerun()
        else:
            st.warning("Selecciona al menos un tema.")

# --- PANTALLA EXAMEN ---
elif s['active'] and not s['end']:
    q = s['qs'][s['idx']]
    
    st.caption(f"Pregunta {s['idx']+1} de {len(s['qs'])} • {q['tema']}")
    st.markdown(f'<p class="pregunta-texto">{q["pregunta"]}</p>', unsafe_allow_html=True)

    if not s['ans']:
        for i, opt in enumerate(q['opciones']):
            if st.button(opt, key=f"btn_{s['idx']}_{i}", use_container_width=True):
                s['choice'] = opt
                s['ans'] = True
                if s['choice'] == q['correcta']: s['score'] += 1
                st.rerun()
    else:
        for opt in q['opciones']:
            if opt == q['correcta']:
                st.markdown(f'<div class="res-box res-correcta">✅ {opt}</div>', unsafe_allow_html=True)
            elif opt == s['choice']:
                st.markdown(f'<div class="res-box res-incorrecta">❌ {opt}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="res-box res-neutral">{opt}</div>', unsafe_allow_html=True)
        
        st.info(f"💡 **Explicación:** {q['explicacion']}")
        
        if st.button("Siguiente Pregunta ➡️", use_container_width=True, type="primary"):
            if s['idx'] + 1 < len(s['qs']):
                s['idx'] += 1; s['ans'] = False; s['choice'] = None; st.rerun()
            else: s['end'] = True; st.rerun()

    st.markdown("<br><hr>", unsafe_allow_html=True)
    if st.button("🏁 Finalizar", type="secondary", use_container_width=True):
        s['end'] = True; st.rerun()

# --- PANTALLA RESULTADOS ---
elif s['end']:
    st.title("🏁 Resultados Finales")
    st.metric("Puntaje", f"{s['score']} / {len(s['qs'])}")
    if st.button("🔄 Volver al inicio", use_container_width=True):
        st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}
        st.rerun()
