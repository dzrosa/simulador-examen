import streamlit as st
import random

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Biología CBC 2026", page_icon="🎓", layout="centered")

# 2. BASE DE DATOS DE PREGUNTAS
def obtener_preguntas_db():
    # NOTA: Agrega aquí todas tus preguntas (mínimo 60 para un examen completo).
    # La primera opción SIEMPRE debe ser la correcta. El código las mezclará solo.
    return [
        {"nro_clase": "1", "tema": "Teoría Celular", "pregunta": "¿Quién propuso que todas las células provienen de otras preexistentes?", "opciones": ["Virchow", "Hooke", "Schleiden", "Schwann"], "explicacion": "Rudolf Virchow completó la teoría celular con este postulado."},
        {"nro_clase": "2", "tema": "Agua", "pregunta": "El agua tiene un alto calor específico porque:", "opciones": ["Puede absorber mucho calor sin cambiar bruscamente de temperatura", "Es una molécula no polar", "Sus enlaces covalentes son débiles", "No forma puentes de hidrógeno"], "explicacion": "Esto permite que el agua actúe como un excelente regulador térmico."},
        {"nro_clase": "3", "tema": "Glúcidos", "pregunta": "¿Cuál es el polisacárido de reserva energética en animales?", "opciones": ["Glucógeno", "Almidón", "Celulosa", "Quitina"], "explicacion": "El glucógeno se almacena principalmente en hígado y músculos."},
        # ... (Copia y pega este formato para llegar a las 60 o más preguntas)
    ]

# 3. TEMARIO PARA EL SELECTOR
TEMARIO = {
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

# 4. ESTILOS CSS
st.markdown("""
    <style>
    .pregunta-texto { font-size: 1.2rem; font-weight: bold; color: #1e293b; margin-bottom: 1.5rem; }
    .res-box { padding: 14px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #cbd5e1; }
    .res-correcta { background-color: #22c55e !important; color: white !important; font-weight: bold; }
    .res-incorrecta { background-color: #ef4444 !important; color: white !important; }
    .res-neutral { background-color: #f8fafc; color: #334155; }
    .resultado-aprobado { color: #22c55e; font-size: 2rem; font-weight: bold; text-align: center; }
    .resultado-reprobado { color: #ef4444; font-size: 2rem; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

if 's' not in st.session_state:
    st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}

s = st.session_state.s

# --- VISTA: INICIO ---
if not s['active'] and not s['end']:
    st.title("🎓 Biología CBC Verano 2026")
    st.subheader("Configura tu práctica (60 preguntas)")
    
    todas = st.checkbox("✅ Practicar con TODOS LOS TEMAS")
    opciones_menu = [f"Clase {k}: {v}" for k, v in TEMARIO.items()]
    
    sel = []
    if not todas:
        sel = st.multiselect("Elegir temas:", options=opciones_menu, placeholder="Selecciona unidades")
    
    if st.button("🚀 EMPEZAR EXAMEN", use_container_width=True, type="primary"):
        db = obtener_preguntas_db()
        
        if todas:
            pool = db
        else:
            numeros = [item.split(":")[0].replace("Clase ", "").strip() for item in sel]
            pool = [p for p in db if p['nro_clase'] in numeros]

        if len(pool) > 0:
            random.shuffle(pool)
            for p in pool:
                p['correcta'] = p['opciones'][0]
                random.shuffle(p['opciones'])
            
            # Tomamos hasta 60 preguntas si existen
            s['qs'] = pool[:60]
            s['active'] = True; s['idx'] = 0; s['score'] = 0; s['ans'] = False
            st.rerun()
        else:
            st.warning("No hay preguntas cargadas para esa selección.")

# --- VISTA: EXAMEN ---
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

# --- VISTA: RESULTADOS ---
elif s['end']:
    st.title("🏁 Fin del Simulacro")
    score = s['score']
    total = len(s['qs'])
    
    st.metric("Aciertos", f"{score} / {total}")
    
    if score >= 36:
        st.markdown('<p class="resultado-aprobado">¡APROBADO! 🎉</p>', unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f'<p class="resultado-reprobado">Sigue practicando... <br> (Necesitas 36/{total})</p>', unsafe_allow_html=True)
    
    if st.button("🔄 Nueva práctica", use_container_width=True):
        st.session_state.s = {'active': False, 'end': False, 'idx': 0, 'score': 0, 'ans': False, 'qs': [], 'choice': None}
        st.rerun()
