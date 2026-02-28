import streamlit as st
import random

# Configuración de página
st.set_page_config(page_title="Biología CBC 2026", page_icon="🎓", layout="centered")

# --- 1. BASE DE DATOS DE PREGUNTAS (FUNCIÓN) ---
def obtener_preguntas():
    # Aquí puedes ir pegando todas tus preguntas del Excel.
    # Formato: {"clase": "1", "pregunta": "...", "opciones": ["Correcta", "Inc1", "Inc2", "Inc3"], "explicacion": "..."}
    # NOTA: Pon siempre la correcta en la PRIMERA posición de la lista "opciones". 
    # El código se encarga de mezclarlas después para que el alumno no lo sepa.
    
    return [
        {
            "clase": "1",
            "pregunta": "¿Cuál es el nivel de organización donde aparece la vida?",
            "opciones": ["Celular", "Macromolecular", "Organular", "Tisular"],
            "explicacion": "La célula es la unidad mínima de la vida (Teoría Celular)."
        },
        {
            "clase": "1",
            "pregunta": "Son características comunes a todos los seres vivos:",
            "opciones": ["Metabolismo, homeostasis y reproducción", "Nutrición autótrofa y movilidad", "Presencia de núcleo y organelas", "Respiración aeróbica obligatoria"],
            "explicacion": "Todos los seres vivos mantienen su medio interno y procesan energía."
        },
        {
            "clase": "3",
            "pregunta": "¿Qué tipo de enlace une a los aminoácidos en una proteína?",
            "opciones": ["Peptídico", "Glucosídico", "Fosfodiéster", "Puente de hidrógeno"],
            "explicacion": "El enlace peptídico es un enlace covalente entre el grupo amino y el carboxilo."
        },
        # Agrega aquí tantas como quieras...
    ]

# --- 2. TEMARIO PARA EL SELECTOR ---
TEMARIO_DETALLADO = {
    "1": "Características de los seres vivos y Teoría celular",
    "2": "Estructura atómica, Agua y pH",
    "3": "Biomoléculas: Glúcidos, Lípidos y Ácidos Nucleicos",
    "4": "Proteínas: Estructura y Función",
    "5": "Bioenergética, Metabolismo y Enzimas",
    # ... agregar el resto de los nombres aquí
}

# --- 3. ESTILOS CSS ---
st.markdown("""
    <style>
    .pregunta-texto { font-size: 1.2rem; font-weight: bold; color: #1e293b; margin-bottom: 1.5rem; }
    .res-box { padding: 14px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #cbd5e1; }
    .res-correcta { background-color: #22c55e !important; color: white !important; font-weight: bold; }
    .res-incorrecta { background-color: #ef4444 !important; color: white !important; }
    .res-neutral { background-color: #f8fafc; color: #334155; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA DE ESTADO ---
if 's' not in st.session_state:
    st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}

s = st.session_state.s

# --- 5. VISTA: INICIO ---
if not s['active'] and not s['end']:
    st.title("🎓 Biología CBC Verano 2026")
    
    opcion_todos = st.checkbox("✅ Practicar con TODOS LOS TEMAS")
    opciones_format = [f"Clase {k}: {v}" for k, v in TEMARIO_DETALLADO.items()]
    
    sel = []
    if not opcion_todos:
        sel = st.multiselect("Elegir temas:", options=opciones_format, placeholder="Selecciona unidades...")
    
    if st.button("🚀 EMPEZAR EXAMEN", use_container_width=True, type="primary"):
        todas_las_preguntas = obtener_preguntas()
        
        if opcion_todos:
            pool = todas_las_preguntas
        else:
            nums = [item.split(":")[0].replace("Clase ", "").strip() for item in sel]
            pool = [p for p in todas_las_preguntas if p['clase'] in nums]

        if pool:
            # MEZCLAR LAS PREGUNTAS
            random.shuffle(pool)
            # MEZCLAR LAS OPCIONES DE CADA PREGUNTA
            for p in pool:
                correcta = p['opciones'][0] # Guardamos la correcta antes de mezclar
                p['correcta'] = correcta
                random.shuffle(p['opciones'])
            
            s['qs'] = pool[:60]
            s['active'] = True; s['idx'] = 0; s['score'] = 0; s['ans'] = False
            st.rerun()

# --- 6. VISTA: EXAMEN ---
elif s['active'] and not s['end']:
    q = s['qs'][s['idx']]
    
    st.caption(f"Pregunta {s['idx']+1} de {len(s['qs'])} • Unidad {q['clase']}")
    st.markdown(f'<p class="pregunta-texto">{q["pregunta"]}</p>', unsafe_allow_html=True)

    if not s['ans']:
        for i, opt in enumerate(q['opciones']):
            if st.button(opt, key=f"b_{s['idx']}_{i}", use_container_width=True):
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

# --- 7. VISTA: RESULTADOS ---
elif s['end']:
    st.title("🏁 Resultados Finales")
    st.metric("Aciertos", f"{s['score']} / {len(s['qs'])}")
    if st.button("🔄 Nueva práctica", use_container_width=True):
        st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}
        st.rerun()
