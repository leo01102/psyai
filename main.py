# main.py

# --- GESTIÓN DE LOGS Y CONFIGURACIÓN INICIAL ---
import streamlit as st
from src.utils.logger_config import setup_logging
setup_logging()

# Usamos session_state para asegurarnos de que la configuración de logging
# se ejecute una sola vez por sesión de usuario, evitando mensajes duplicados.
if 'logging_configured' not in st.session_state:
    setup_logging()
    st.session_state.logging_configured = True

import logging
from collections import deque
import cv2
import av
import threading
from typing import List

# Importar módulos del proyecto
from src.analysis.facial_emotion import initialize_detector, analyze_frame_emotions
from src.analysis.voice_transcription import run_transcription # MODIFICADO
from src.analysis.voice_emotion import get_recognizer # NUEVO
from src.chat.llm_client import get_groq_response, extract_memory_from_text
from src.audio.tts_player import run_synthesis
from src.chat.prompt_builder import build_llm_prompt, build_memory_extraction_prompt
from src.database.data_manager import setup_database, start_new_session, save_interaction_encrypted, save_memory_fact, get_all_memory
from src.ui.components import render_video_feed, render_facial_emotion_component, render_vocal_emotion_component, render_chat_history, render_audio_player
from audiorecorder import audiorecorder

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="PsyAI - Sesión en Tiempo Real", layout="wide")
st.title("🧠 PsyAI - Sesión en Tiempo Real")

# Constantes
FRAME_SKIP = 5
BUFFER_SIZE = 10

# Cargar recursos (modelos, conexión DB)
@st.cache_resource
def load_resources():
    logging.info("Cargando recursos (modelos, DB)...")
    facial_detector = initialize_detector()
    vocal_recognizer = get_recognizer(method="onnx_fp32") # NUEVO: Cargar modelo vocal
    setup_database()
    logging.info("Recursos cargados exitosamente.")
    return facial_detector, vocal_recognizer

facial_detector, vocal_recognizer = load_resources()

# --- Estructura Segura para Comunicación entre Hilos ---
class AnalysisResult:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()
    def set_data(self, key, value):
        with self.lock:
            self.data[key] = value
    def get_data(self, key=None):
        with self.lock:
            if key:
                return self.data.get(key)
            return self.data.copy()

# Inicialización del estado de sesión
if "session_id" not in st.session_state:
    st.session_state.session_id = start_new_session()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ai_audio" not in st.session_state:
    st.session_state.ai_audio = None
if "long_term_memory" not in st.session_state:
    st.session_state.long_term_memory = get_all_memory()
if "analysis_result_container" not in st.session_state:
    st.session_state.analysis_result_container = AnalysisResult()
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# --- PROCESADOR DE VIDEO ---
class EmotionProcessor:
    def __init__(self, detector, result_container: AnalysisResult):
        self.detector = detector
        self.result_container = result_container
        self.frame_counter = 0
        self.emotion_buffer = deque(maxlen=BUFFER_SIZE)

    def _aggregate_emotions(self):
        if not self.emotion_buffer: return None
        avg_scores = {e: sum(d['scores'][e] for d in self.emotion_buffer) / len(self.emotion_buffer) for e in self.emotion_buffer[0]['scores']}
        dominant_emotions = [d['dominant_emotion'] for d in self.emotion_buffer]
        most_common_dominant = max(set(dominant_emotions), key=dominant_emotions.count)
        return {"stable_dominant_emotion": most_common_dominant, "average_scores": avg_scores}

    async def recv_queued(self, frames: List[av.VideoFrame]) -> List[av.VideoFrame]:
        if not frames: return []
        latest_frame = frames[-1]
        img = latest_frame.to_ndarray(format="bgr24")
        self.frame_counter += 1
        if self.frame_counter % FRAME_SKIP == 0:
            result = analyze_frame_emotions(self.detector, img)
            if result:
                self.emotion_buffer.append(result)
                aggregated_result = self._aggregate_emotions()
                self.result_container.set_data("facial_emotion", aggregated_result)
        
        last_detection = self.emotion_buffer[-1] if self.emotion_buffer else None
        if last_detection:
            (x, y, w, h) = last_detection["bounding_box"]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, last_detection["dominant_emotion"].capitalize(), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        return [av.VideoFrame.from_ndarray(img, format="bgr24")]

# --- LAYOUT DE LA UI ---
if facial_detector is None or vocal_recognizer is None:
    st.error("Error al cargar uno de los modelos de IA. La aplicación no puede continuar.")
    logging.error("Detector facial o reconocedor vocal no se inicializó. Terminando la ejecución de la UI.")
else:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Interacción")
        audio_bytes = audiorecorder("Mantén presionado para hablar", "Suelta para enviar...")

        chat_container = st.container(height=400)
        with chat_container:
            render_chat_history()
        render_audio_player()

    with col2:
        st.header("Análisis de Emociones")
        result_container = st.session_state.analysis_result_container
        
        def processor_factory():
            return EmotionProcessor(detector=facial_detector, result_container=result_container)

        webrtc_ctx = render_video_feed(processor_factory, async_processing=True)
        
        # Contenedores para los resultados
        facial_emotion_placeholder = st.empty()
        vocal_emotion_placeholder = st.empty()
        
        with facial_emotion_placeholder.container():
             render_facial_emotion_component(result_container.get_data("facial_emotion"))
        with vocal_emotion_placeholder.container():
             render_vocal_emotion_component(result_container.get_data("vocal_emotion"))

    # --- CICLO DE CONVERSACIÓN ---
    if len(audio_bytes) > 0 and audio_bytes != st.session_state.last_processed_audio:
        st.session_state.last_processed_audio = audio_bytes
        
        with st.spinner("Procesando tu voz..."):
            wav_audio_data = audio_bytes.export(format="wav").read()
            
            # 1. Transcribir
            user_text = run_transcription(wav_audio_data)
            
            # 2. NUEVO: Analizar emoción vocal
            vocal_emotions_result = vocal_recognizer.predict(wav_audio_data)
            st.session_state.analysis_result_container.set_data("vocal_emotion", {"vocal_emotions": vocal_emotions_result})
            logging.info(f"Emoción vocal detectada: {vocal_emotions_result[0] if vocal_emotions_result else 'Ninguna'}")
            
            if user_text and user_text.strip() != "":
                facial_emotion_data = st.session_state.analysis_result_container.get_data("facial_emotion")
                
                logging.info(f"Usuario transcribió: '{user_text}'")                
                st.session_state.messages.append({"role": "user", "content": user_text})
                
                # Combinar datos de emoción para guardar y para el prompt
                user_interaction_data = {
                    "text": user_text,
                    "facial_dominant": facial_emotion_data.get("stable_dominant_emotion") if facial_emotion_data else None,
                    "facial_scores": facial_emotion_data.get("average_scores") if facial_emotion_data else None,
                    "vocal_analysis": vocal_emotions_result # NUEVO
                }
                save_interaction_encrypted(st.session_state.session_id, 'user', user_interaction_data)
                
                # 3. Construir Prompt y Obtener Respuesta
                prompt_context_data = {
                    "facial_dominant": user_interaction_data["facial_dominant"],
                    "vocal_emotions": vocal_emotions_result
                }
                prompt_messages = build_llm_prompt(st.session_state.messages, user_text, prompt_context_data, st.session_state.long_term_memory)
                ai_response = get_groq_response(prompt_messages)
                logging.info(f"IA respondió: '{ai_response}'")
                
                # 4. Extraer Memoria
                memory_prompt = build_memory_extraction_prompt(user_text, ai_response)
                extracted_facts = extract_memory_from_text(memory_prompt)
                if extracted_facts:
                    logging.info(f"Hechos de memoria extraídos: {extracted_facts}")
                    for key, value in extracted_facts.items():
                        save_memory_fact(key, value)
                        st.session_state.long_term_memory[key] = value

                # 5. Sintetizar Audio y Guardar respuesta de la IA
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                save_interaction_encrypted(st.session_state.session_id, 'assistant', {"text": ai_response})
                st.session_state.ai_audio = run_synthesis(ai_response)
                
                st.rerun()
            else:
                st.error("Lo siento, no pude entender lo que dijiste. ¿Podrías intentarlo de nuevo?")
                logging.warning("La transcripción falló o devolvió un texto vacío.")