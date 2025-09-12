# backend/config.py | Archivo de configuración (ej: URL de la API de LM Studio, timeouts)

import os
from dotenv import load_dotenv

load_dotenv()

# API keys
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Encryption Key
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not all([DEEPGRAM_API_KEY, GROQ_API_KEY, ENCRYPTION_KEY]):
    raise ValueError("Faltan una o más variables de entorno. Asegúrate de que DEEPGRAM_API_KEY, GROQ_API_KEY, y ENCRYPTION_KEY están definidas en tu archivo .env.")

# Configuraciones no secretas
EDGE_VOICE = "es-CO-SalomeNeural"
