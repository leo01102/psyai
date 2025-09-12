# backend/src/chat/prompt_builder.py

def build_llm_prompt(chat_history: list, latest_user_text: str, emotion_data: dict, long_term_memory: dict) -> list:
    """Construye la lista de mensajes para el LLM, incluyendo historia y contexto."""
    
    system_prompt = (
        "Eres L, un asistente de IA compasivo y empático. Tu objetivo es escuchar, "
        "ofrecer apoyo y mantener una conversación constructiva. Responde de forma concisa "
        "y natural. No des consejos médicos. Si detectas un riesgo (autolesión, etc.), "
        "recomienda buscar ayuda profesional inmediatamente."
    )
    
    # Añadir memoria a largo plazo al contexto
    if long_term_memory:
        memory_str = "\n".join([f"- {key.replace('_', ' ').capitalize()}: {value}" for key, value in long_term_memory.items()])
        system_prompt += f"\n\n### Datos clave recordados sobre el usuario:\n{memory_str}"

    # Construir el prompt del usuario con contexto emocional multimodal
    facial_emotion = emotion_data.get('facial_dominant', 'neutral')
    vocal_emotion_data = emotion_data.get('vocal_emotions', [])
    
    # Seleccionar la emoción vocal más probable
    vocal_emotion = vocal_emotion_data[0]['label'].lower() if vocal_emotion_data else 'desconocido'
    
    emotional_context = (
        f"Contexto emocional detectado:\n"
        f"- Expresión facial: {facial_emotion.capitalize()}\n"
        f"- Tono de voz: {vocal_emotion.capitalize()}"
    )
    
    final_user_content = f"{emotional_context}\n\nMensaje del usuario: \"{latest_user_text}\""
    
    # Construir el historial completo para enviar a la API
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": final_user_content})
    
    return messages

def build_memory_extraction_prompt(user_text: str, ai_response: str) -> str:
    """Construye un prompt para que el LLM extraiga hechos en formato JSON."""
    
    prompt = (
        "Analiza la siguiente conversación y extrae hechos clave sobre el usuario. "
        "Devuelve SÓLO un objeto JSON. Claves válidas son: 'nombre', 'edad', "
        "'tema_recurrente', 'preferencia_personal', 'meta_u_objetivo'. "
        "Si no se mencionan hechos nuevos o relevantes, devuelve un JSON vacío {}."
        "\n--- CONVERSACIÓN ---"
        f"\nUsuario: \"{user_text}\""
        f"\nPsyAI: \"{ai_response}\""
        "\n--- FIN DE LA CONVERSACIÓN ---"
        "\nJSON extraído:"
    )
    return prompt