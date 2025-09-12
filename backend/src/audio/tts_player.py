# backend/src/audio/tts_player.py

import asyncio
import os
import tempfile
from edge_tts import Communicate
from pydub import AudioSegment
import config

async def synthesize_speech_edge(text: str):
    """
    Sintetiza el texto a voz usando Edge-TTS y devuelve los datos de audio en bytes.
    """
    try:
        communicate = Communicate(text, config.EDGE_VOICE)
        
        # Guardar en un archivo temporal para procesarlo con pydub
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_path = tmp_file.name

        await communicate.save(tmp_path)
        
        # Aumentar volumen y leer los bytes
        audio = AudioSegment.from_file(tmp_path, format="mp3")
        audio = audio.apply_gain(+6)
        
        # Exportar a un buffer en memoria
        buffer = audio.export(format="mp3").read()

        # Limpiar el archivo temporal
        os.remove(tmp_path)
        
        return buffer

    except Exception as e:
        print(f"Error durante la síntesis de voz: {e}")
        return None

# Función de conveniencia para ejecutar desde Streamlit
def run_synthesis(text: str) -> bytes:
    return asyncio.run(synthesize_speech_edge(text))
