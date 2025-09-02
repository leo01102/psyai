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
import asyncio

# Importar módulos del proyecto
from src.analysis.facial_emotion import initialize_detector, analyze_frame_emotions
from src.analysis.voice_emotion import run_transcription
from src.chat.llm_client import get_groq_response, extract_memory_from_text
from src.audio.tts_player import run_synthesis
from src.chat.prompt_builder import build_llm_prompt, build_memory_extraction_prompt
from src.database.data_manager import setup_database, start_new_session, save_interaction_encrypted, save_memory_fact, get_all_memory
from src.ui.components import render_video_feed, render_emotion_analysis_component, render_chat_history, render_audio_player
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
    detector = initialize_detector()
    setup_database()
    logging.info("Recursos cargados exitosamente.")
    return detector

detector = load_resources()

# --- Estructura Segura para Comunicación entre Hilos ---
class AnalysisResult:
    def __init__(self):
        self.aggregated_data = None
        self.lock = threading.Lock()
    def set_data(self, data):
        with self.lock:
            self.aggregated_data = data
    def get_data(self):
        with self.lock:
            return self.aggregated_data

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

    # --- MÉTODO ASÍNCRONO recv_queued ---
    async def recv_queued(self, frames: List[av.VideoFrame]) -> List[av.VideoFrame]:
        # Si no hay fotogramas, devolvemos una lista vacía.
        if not frames:
            return []

        # Saltamos la mayoría de los fotogramas, procesando solo el más reciente.
        latest_frame = frames[-1]
        img = latest_frame.to_ndarray(format="bgr24")

        # Mantenemos nuestro propio contador para limitar el análisis de la IA
        self.frame_counter += 1
        if self.frame_counter % FRAME_SKIP == 0:
            # Simulamos una operación de larga duración (como el análisis de IA)
            # await asyncio.sleep(0.05) # Descomentar para pruebas de carga
            
            result = analyze_frame_emotions(self.detector, img)
            if result:
                self.emotion_buffer.append(result)
                aggregated_result = self._aggregate_emotions()
                self.result_container.set_data(aggregated_result)
        
        # Dibujar en el fotograma
        last_detection = self.emotion_buffer[-1] if self.emotion_buffer else None
        if last_detection:
            (x, y, w, h) = last_detection["bounding_box"]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, last_detection["dominant_emotion"].capitalize(), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Devolvemos el fotograma modificado en una lista.
        return [av.VideoFrame.from_ndarray(img, format="bgr24")]

# --- LAYOUT DE LA UI ---
if detector is None:
    st.error("Error al cargar el modelo de detección facial. La aplicación no puede continuar.")
    logging.error("Detector FER no se inicializó. Terminando la ejecución de la UI.")
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
        # 1. Obtenemos el contenedor del estado de la sesión ANTES de pasarlo.
        result_container = st.session_state.analysis_result_container

        # 2. Creamos una función factory que captura el contenedor ya existente.
        #    La lambda ahora no necesita acceder a st.session_state directamente.
        def processor_factory():
            return EmotionProcessor(detector=detector, result_container=result_container)

        # 3. Pasamos esta factory segura al componente de video, e indicamos que el procesador es asíncrono.
        webrtc_ctx = render_video_feed(
            processor_factory,
            async_processing=True # Le decimos a webrtc_streamer que use el modo asíncrono
        )
        
        if webrtc_ctx.state.playing:
             # Leemos del contenedor seguro para mostrar los datos.
             current_emotion_data = result_container.get_data()
             render_emotion_analysis_component(current_emotion_data)

    # --- CICLO DE CONVERSACIÓN ---
    # Solo procesamos si hay un audio NUEVO que no hemos procesado antes.
    if len(audio_bytes) > 0 and audio_bytes != st.session_state.last_processed_audio:
        # GUARDAMOS EL AUDIO ACTUAL PARA EVITAR RE-PROCESARLO
        st.session_state.last_processed_audio = audio_bytes
        with st.spinner("Procesando tu voz..."):
            # El objeto 'audio_bytes' de audiorecorder es en realidad un objeto Pydub.
            # Necesitamos exportar su contenido a bytes en formato WAV para Deepgram.
            wav_audio_data = audio_bytes.export(format="wav").read()
            
            # 1. Transcribir
            user_text = run_transcription(wav_audio_data)
            
            # --- BLOQUE DE CONTROL DE ERRORES ---
            if user_text is not None and user_text.strip() != "":
                current_emotion_data = st.session_state.analysis_result_container.get_data()
                
                logging.info(f"Usuario transcribió: '{user_text}'")                
                # Guardar la interacción del usuario
                st.session_state.messages.append({"role": "user", "content": user_text})
                
                # Pasar los datos de emoción de forma estructurada
                user_interaction_data = {
                    "text": user_text,
                    "facial_dominant": current_emotion_data.get("stable_dominant_emotion") if current_emotion_data else None,
                    "facial_scores": current_emotion_data.get("average_scores") if current_emotion_data else None
                }
                save_interaction_encrypted(st.session_state.session_id, 'user', user_interaction_data)
                
                # 2. Construir Prompt y Obtener Respuesta
                prompt_messages = build_llm_prompt(st.session_state.messages, user_text, current_emotion_data, st.session_state.long_term_memory)
                ai_response = get_groq_response(prompt_messages)
                logging.info(f"IA respondió: '{ai_response}'")
                
                # 3. Extraer Memoria
                memory_prompt = build_memory_extraction_prompt(user_text, ai_response)
                extracted_facts = extract_memory_from_text(memory_prompt)
                if extracted_facts:
                    logging.info(f"Hechos de memoria extraídos: {extracted_facts}")
                    for key, value in extracted_facts.items():
                        save_memory_fact(key, value)
                        st.session_state.long_term_memory[key] = value

                # 4. Sintetizar Audio y Guardar respuesta de la IA
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                save_interaction_encrypted(st.session_state.session_id, 'assistant', {"text": ai_response})
                st.session_state.ai_audio = run_synthesis(ai_response)
                
                st.rerun()
            else:
                # Si la transcripción falla, muestra un error en la UI
                st.error("Lo siento, no pude entender lo que dijiste. ¿Podrías intentarlo de nuevo?")
                logging.warning("La transcripción falló o devolvió un texto vacío.")
