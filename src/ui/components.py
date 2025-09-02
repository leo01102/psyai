# src/ui/components.py

import streamlit as st
import time
from streamlit_webrtc import webrtc_streamer

def render_video_feed(processor_factory, async_processing: bool = False):
    """Renderiza el componente de la cámara y el análisis en vivo."""
    st.header("Análisis en Vivo")
    webrtc_ctx = webrtc_streamer(
        key="emotion-analysis",
        video_processor_factory=processor_factory,
        async_processing=async_processing,
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    return webrtc_ctx

def render_emotion_analysis_component(agg_result):
    """
    Renderiza el componente de análisis emocional UNA SOLA VEZ.
    """
    st.header("Estado Emocional Agregado")
    placeholder = st.empty()
    
    with placeholder.container():
        st.subheader("Expresión Facial Estable")
        if agg_result:
            st.metric("Emoción Dominante", agg_result["stable_dominant_emotion"].capitalize())
            st.write("Puntuaciones Promedio:")
            
            st.dataframe(
                {"Emoción": agg_result["average_scores"].keys(),
                 "Confianza Promedio": [f"{s:.1%}" for s in agg_result["average_scores"].values()]},
                width='stretch'
            )
        else:
            st.warning("Analizando... No se detecta ninguna cara.")

def render_emotion_analysis(result_container, webrtc_ctx):
    """Renderiza el display de análisis emocional agregado."""
    st.header("Estado Emocional Agregado")
    placeholder = st.empty()
    
    while webrtc_ctx and webrtc_ctx.state.playing:
        agg_result = result_container.get_data()
        with placeholder.container():
            st.subheader("Expresión Facial Estable")
            if agg_result:
                st.metric("Emoción Dominante", agg_result["stable_dominant_emotion"].capitalize())
                st.dataframe(
                    {"Emoción": agg_result["average_scores"].keys(),
                     "Confianza Promedio": [f"{s:.1%}" for s in agg_result["average_scores"].values()]},
                    use_container_width=True
                )
            else:
                st.warning("Analizando... No se detecta ninguna cara.")
        time.sleep(0.5)

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
