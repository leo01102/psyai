# backend/tests/integration/test_apis.py

import sys
import os
from pathlib import Path
REPO_ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parents[1]
sys.path.insert(0, str(REPO_ROOT))

import asyncio
from src.analysis.voice_emotion import transcribe_audio_deepgram
from src.chat.llm_client import get_groq_response
from src.chat.prompt_builder import build_llm_prompt

# --- Configuración de prueba ---
AUDIO_FILE_PATH = REPO_ROOT / "tests" / "fixtures" / "short_spanish_test.wav"
TEST_USER_TEXT = "Hola, esta es una prueba para ver si la transcripción y el LLM funcionan."

# --- Función principal ---
async def main_test():
    print("--- INICIANDO PRUEBA DE APIs ---")

    # 1. Prueba de Deepgram (transcripción)
    print("\n[Paso 1: Probando Deepgram]")
    user_text_from_audio = None
    try:
        with open(AUDIO_FILE_PATH, "rb") as audio_file:
            audio_bytes = audio_file.read()
            user_text_from_audio = await transcribe_audio_deepgram(audio_bytes)
        
        if user_text_from_audio:
            print(f"✅ Éxito en la transcripción: '{user_text_from_audio}'")
        else:
            print("❌ Fallo en la transcripción: Deepgram devolvió una cadena vacía.")
    except FileNotFoundError:
        print(f"⚠️ No se encontró '{AUDIO_FILE_PATH}'. Usando texto de prueba manual.")
        user_text_from_audio = TEST_USER_TEXT
    except Exception as e:
        print(f"❌ Fallo crítico en la transcripción: {e}")
        return

    # 2. Prueba de Groq (LLM)
    print("\n[Paso 2: Probando Groq]")
    if user_text_from_audio:
        mock_emotion_data = {"stable_dominant_emotion": "neutral"}
        mock_memory = {"nombre": "Leo"}
        
        prompt_messages = build_llm_prompt([], user_text_from_audio, mock_emotion_data, mock_memory)
        
        print("Enviando prompt a Groq...")
        ai_response = get_groq_response(prompt_messages)
        
        if ai_response and "Error:" not in ai_response:
            print("✅ Éxito en la respuesta del LLM:")
            print(f"-> {ai_response}")
        else:
            print("❌ Fallo en la respuesta del LLM.")
            print(f"-> Respuesta recibida: {ai_response}")
    
    print("\n--- PRUEBA FINALIZADA ---")

if __name__ == "__main__":
    asyncio.run(main_test())
