# backend/api.py

import logging
import base64
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
from src.utils.logger_config import setup_logging
setup_logging()

from src.analysis.facial_emotion import initialize_detector, analyze_frame_emotions
from src.analysis.voice_transcription import run_transcription
from src.analysis.voice_emotion import get_recognizer
from src.chat.llm_client import get_groq_response, extract_memory_from_text
from src.audio.tts_player import run_synthesis
from src.chat.prompt_builder import build_llm_prompt, build_memory_extraction_prompt
from src.database.data_manager import setup_database, start_new_session, save_interaction_encrypted, save_memory_fact, get_all_memory

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="PsyAI Backend API",
    version="1.0.0",
    description="API para el asistente emocional multimodal Lumen."
)

# --- MIDDLEWARE (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Origen del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Carga de Modelos (Singleton en el estado de la app) ---
@app.on_event("startup")
def load_models_on_startup():
    """Carga los modelos pesados una sola vez cuando el servidor arranca."""
    logging.info("Cargando modelos de IA en memoria...")
    app.state.facial_detector = initialize_detector()
    app.state.vocal_recognizer = get_recognizer(method="onnx_fp32")
    setup_database()
    if app.state.facial_detector and app.state.vocal_recognizer:
        logging.info("Modelos y base de datos listos.")
    else:
        logging.error("¡FALLO CRÍTICO AL CARGAR MODELOS! La API puede no funcionar correctamente.")

# --- Modelos de Datos (Pydantic) para Validación ---
class EmotionPayload(BaseModel):
    stable_dominant_emotion: str | None = None
    average_scores: Dict[str, float] | None = None

class InteractionRequest(BaseModel):
    session_id: int
    audio_b64: str
    facial_emotion: EmotionPayload | None = None
    chat_history: List[Dict[str, str]]
    long_term_memory: Dict[str, Any]

class InteractionResponse(BaseModel):
    ai_text: str
    ai_audio_b64: str | None
    extracted_memory: Dict[str, Any]
    updated_chat_history: List[Dict[str, str]]

# --- ENDPOINTS DE LA API ---

@app.get("/")
def read_root():
    """Endpoint raíz para verificar que la API está viva."""
    return {"status": "Lumen Backend está funcionando."}

@app.post("/session", status_code=201)
def create_new_session():
    """Crea una nueva sesión de chat y devuelve su ID."""
    session_id = start_new_session()
    if session_id is None:
        raise HTTPException(status_code=500, detail="No se pudo crear la sesión en la base de datos.")
    logging.info(f"Nueva sesión creada con ID: {session_id}")
    return {"session_id": session_id}

@app.post("/interact", response_model=InteractionResponse)
def process_interaction(request: InteractionRequest, http_request: Request):
    """Endpoint principal: recibe audio y contexto, devuelve la respuesta de la IA."""
    logging.info(f"Procesando interacción para la sesión {request.session_id}...")
    
    facial_detector = http_request.app.state.facial_detector
    vocal_recognizer = http_request.app.state.vocal_recognizer
    
    if not all([facial_detector, vocal_recognizer]):
        raise HTTPException(status_code=503, detail="Servicio no disponible: los modelos de IA no están cargados.")

    try:
        audio_bytes = base64.b64decode(request.audio_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Error al decodificar el audio base64.")

    # 1. Análisis en paralelo
    user_text = run_transcription(audio_bytes)
    vocal_emotion_data = vocal_recognizer.predict(audio_bytes)

    if not user_text or not user_text.strip():
        raise HTTPException(status_code=400, detail="La transcripción falló o el audio estaba vacío.")

    # 2. Guardar interacción del usuario
    facial_emotion_data = request.facial_emotion.dict() if request.facial_emotion else {}
    user_interaction_data = {
        "text": user_text,
        "facial_dominant": facial_emotion_data.get("stable_dominant_emotion"),
        "facial_scores": facial_emotion_data.get("average_scores"),
        "vocal_analysis": vocal_emotion_data
    }
    save_interaction_encrypted(request.session_id, 'user', user_interaction_data)
    
    # 3. Construir prompt y obtener respuesta del LLM
    prompt_context_data = {
        "facial_dominant": user_interaction_data["facial_dominant"],
        "vocal_emotions": vocal_emotion_data
    }
    updated_chat_history = request.chat_history + [{"role": "user", "content": user_text}]
    prompt_messages = build_llm_prompt(updated_chat_history, user_text, prompt_context_data, request.long_term_memory)
    ai_response_text = get_groq_response(prompt_messages)
    
    # 4. Extraer y guardar memoria
    memory_prompt = build_memory_extraction_prompt(user_text, ai_response_text)
    extracted_facts = extract_memory_from_text(memory_prompt)
    if extracted_facts:
        for key, value in extracted_facts.items():
            save_memory_fact(key, value)
    
    # 5. Guardar interacción de la IA
    save_interaction_encrypted(request.session_id, 'assistant', {"text": ai_response_text})
    
    # 6. Sintetizar audio
    ai_audio_bytes = run_synthesis(ai_response_text)
    ai_audio_b64 = base64.b64encode(ai_audio_bytes).decode('utf-8') if ai_audio_bytes else None
    
    # 7. Devolver respuesta completa
    final_chat_history = updated_chat_history + [{"role": "assistant", "content": ai_response_text}]
    
    return InteractionResponse(
        ai_text=ai_response_text,
        ai_audio_b64=ai_audio_b64,
        extracted_memory=extracted_facts,
        updated_chat_history=final_chat_history
    )