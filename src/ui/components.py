# src/ui/components.py

import streamlit as st
import time
from streamlit_webrtc import webrtc_streamer

def render_video_feed(processor_factory, async_processing: bool = False):
    """Renderiza el componente de la cámara y el análisis en vivo."""
    st.header("Análisis Facial en Vivo")
    webrtc_ctx = webrtc_streamer(
        key="emotion-analysis",
        video_processor_factory=processor_factory,
        async_processing=async_processing,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    return webrtc_ctx

def render_facial_emotion_component(agg_result):
    """Renderiza el componente de análisis de emoción facial."""
    st.subheader("Expresión Facial Estable")
    if agg_result:
        st.metric("Emoción Dominante", agg_result["stable_dominant_emotion"].capitalize())
        df_data = {
            "Emoción": list(agg_result["average_scores"].keys()),
            "Confianza Promedio": [f"{s:.1%}" for s in agg_result["average_scores"].values()]
        }
        # CORREGIDO: Eliminamos el argumento deprecado. El comportamiento por defecto es estirar.
        st.dataframe(df_data, hide_index=True)
    else:
        st.warning("Analizando... No se detecta ninguna cara.")

def render_vocal_emotion_component(vocal_result):
    """Renderiza el componente de análisis de emoción vocal."""
    st.subheader("Análisis de Emoción Vocal")
    if vocal_result and "vocal_emotions" in vocal_result and vocal_result["vocal_emotions"]:
        top_emotion = vocal_result["vocal_emotions"][0]
        st.metric("Emoción Principal Detectada", f"{top_emotion['label']} ({top_emotion['score']:.1%})")
        
        df_data = {
            "Emoción": [e['label'] for e in vocal_result["vocal_emotions"]],
            "Confianza": [f"{e['score']:.1%}" for e in vocal_result["vocal_emotions"]]
        }
        # CORREGIDO: Eliminamos el argumento deprecado.
        st.dataframe(df_data, hide_index=True)
    else:
        st.info("Esperando audio para analizar la emoción vocal.")

def render_chat_history():
    """Renderiza el historial de mensajes del chat."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def render_audio_player():
    """Renderiza el reproductor de audio si hay audio de IA para reproducir."""
    if st.session_state.ai_audio:
        st.audio(st.session_state.ai_audio, format="audio/mp3", autoplay=True)
        # Limpiar después de renderizar para que no se reproduzca en cada rerun
        st.session_state.ai_audio = None