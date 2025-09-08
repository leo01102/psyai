# src/analysis/voice_transcription.py | Lógica para transcribir voz a texto

from deepgram import Deepgram
import asyncio
import config

# Inicializar el cliente de Deepgram
try:
    dg_client = Deepgram(config.DEEPGRAM_API_KEY)
except Exception as e:
    print(f"Error al inicializar el cliente de Deepgram: {e}")
    dg_client = None

async def transcribe_audio_deepgram(audio_data: bytes) -> str | None:
    """
    Transcribe audio usando Deepgram. Devuelve el texto o None en caso de error.
    """
    if not dg_client:
        print("Error: El cliente de Deepgram no está inicializado.")
        return None

    try:
        source = {"buffer": audio_data, "mimetype": "audio/wav"}
        response = await dg_client.transcription.prerecorded(
            source, 
            {"punctuate": True, "language": "es", "model": "nova-3", "smart_format": True}
        )
        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        return transcript
    except Exception as e:
        print(f"Error durante la transcripción con Deepgram: {e}")
        return None # Devolver None es una señal de error explícita
        
def run_transcription(audio_data: bytes) -> str | None:
    """Función de conveniencia para ejecutar el código asíncrono desde Streamlit."""
    return asyncio.run(transcribe_audio_deepgram(audio_data))