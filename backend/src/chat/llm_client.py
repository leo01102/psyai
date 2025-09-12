# backend/src/chat/llm_client.py

from groq import Groq
import config
import json

try:
    groq_client = Groq(api_key=config.GROQ_API_KEY)
except Exception as e:
    print(f"Error al inicializar el cliente de Groq: {e}")
    groq_client = None

def get_groq_response(messages: list):
    """Envía una lista de mensajes al LLM de Groq y devuelve la respuesta."""
    if not groq_client:
        return "Error: Cliente de Groq no inicializado."
    try:
        response = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant"
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error al comunicarse con la API de Groq: {e}")
        return "Lo siento, tuve un problema al generar una respuesta."

def extract_memory_from_text(prompt: str) -> dict:
    """Envía un prompt de extracción y espera una respuesta JSON."""
    if not groq_client:
        return {}
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except (json.JSONDecodeError, IndexError, TypeError, Exception) as e:
        print(f"Error al extraer o parsear memoria JSON: {e}")
        return {}
