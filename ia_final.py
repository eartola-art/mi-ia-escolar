import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import json
import os

# 1. CONFIGURACIÓN Y ESTILO PROFESIONAL
st.set_page_config(page_title="Kaixo Endika Artola", page_icon="🎓", layout="wide")

# Estilo para el botón de Reset en rojo y diseño limpio
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 10px; width: 100%; border: 1px solid #d33; color: white; background-color: #ff4b4b; }
    .stButton>button:hover { background-color: #bd3636; border-color: #bd3636; }
    </style>
    """, unsafe_allow_html=True)

# TÍTULO PERSONALIZADO
st.title("🤖 Kaixo Endika Artola")
st.markdown("---")

# 2. GESTIÓN DE MEMORIA (ARCHIVO JSON)
ARCHIVO_HISTORIAL = "historial_chat.json"

def cargar_historial():
    if os.path.exists(ARCHIVO_HISTORIAL):
        with open(ARCHIVO_HISTORIAL, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_historial(mensajes):
    with open(ARCHIVO_HISTORIAL, "w", encoding="utf-8") as f:
        json.dump(mensajes, f, ensure_ascii=False, indent=4)

if "messages" not in st.session_state:
    st.session_state.messages = cargar_historial()

# 3. BARRA LATERAL (MODOS Y RESET)
with st.sidebar:
    st.header("⚙️ Opciones")
    api_key = st.text_input("Introduce tu Groq API Key", type="password")
    
    st.write("---")
    
    # LOS CUATRO MODOS (Añadido 'Conversación')
    modo = st.selectbox("🎯 Elige el tipo de respuesta:", 
                        ["Conversación", "Explicación", "Resumen", "Modo Examen"])
    
    # Lógica de comportamiento para cada modo
    instrucciones = {
        "Conversación": "Eres un asistente útil y amable. Responde de forma natural y ayuda en lo que necesite el usuario en su idioma.",
        "Explicación": "Eres un profesor. Explica el tema que te den con detalle, ejemplos y lenguaje sencillo. Responde siempre en el idioma del usuario.",
        "Resumen": "Tu único objetivo es resumir. Usa listas de puntos, negritas y esquemas. Sé breve y directo. Responde siempre en el idioma del usuario.",
        "Modo Examen": "No des respuestas. Hazle una pregunta al usuario sobre el tema para evaluarlo. Responde siempre en el idioma del usuario."
    }
    
    st.write("---")
    # BOTÓN RESET CONVERSACIÓN
    if st.button("🗑️ Reset Conversación"):
        st.session_state.messages = []
        if os.path.exists(ARCHIVO_HISTORIAL):
            os.remove(ARCHIVO_HISTORIAL)
        st.rerun()

# 4. CHAT
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe aquí tu duda..."):
    if not api_key:
        st.warning("⚠️ Introduce tu clave API a la izquierda.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            with st.chat_message("assistant"):
                llm = ChatGroq(
                    groq_api_key=api_key, 
                    model_name="llama-3.3-70b-versatile"
                )
                
                mensajes_ia = [SystemMessage(content=instrucciones[modo])]
                
                for m in st.session_state.messages:
                    if m["role"] == "user":
                        mensajes_ia.append(HumanMessage(content=m["content"]))
                    else:
                        mensajes_ia.append(AIMessage(content=m["content"]))
                
                response = llm.invoke(mensajes_ia)
                st.markdown(response.content)
                
                st.session_state.messages.append({"role": "assistant", "content": response.content})
                guardar_historial(st.session_state.messages)
        
        except Exception as e:
            st.error(f"Error: {e}")









