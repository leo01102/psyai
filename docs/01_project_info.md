### **1. Información General del Proyecto**

*   **Nombre del Proyecto:** PsyAI - Psicólogo con IA Emocional
*   **Misión:** Desarrollar un asistente psicológico basado en IA que ofrezca un apoyo más empático y efectivo mediante la detección en tiempo real de las emociones faciales y vocales del usuario.
*   **Tecnología Principal de IA:** Se utilizará el modelo de lenguaje `Mistral 7B` ejecutado localmente a través de `LM Studio` para la parte conversacional.
*   **Propuesta de Valor:** A diferencia de los chatbots tradicionales, este proyecto integra análisis emocional multimodal (cara y voz) para adaptar sus respuestas, cubriendo una necesidad en el campo de la salud mental accesible.

---

### **2. Producto Mínimo Viable (MVP)**

*   **Captura de Video:** La aplicación accederá a la webcam del usuario para capturar su rostro en tiempo real.
*   **Detección de Emociones Faciales:** Un modelo preentrenado identificará emociones básicas (alegría, tristeza, enojo, sorpresa, neutralidad).
*   **Interfaz de Usuario Sencilla:** Una aplicación local mostrará el video en vivo y un cuadro de texto con la emoción detectada.
*   **Respuesta Empática Básica:** El bot responderá con mensajes simples basados en la emoción detectada. Ejemplo: "Veo que te sientes triste. ¿Te gustaría hablar de ello?".

---

### **3. Arquitectura y Stack Tecnológico**

#### Backend y Lógica de IA

| Rol | Herramienta |
| :--- | :--- |
| **Lenguaje y Entorno de Ejecución** | Python |
| **IA Conversacional (LLM)** | LM Studio sirviendo el modelo Mistral 7B (API local) |
| **Detección de Emoción Facial** | `fer`, `deepface` u otras librerías preentrenadas |
| **Captura y Procesamiento de Video** | `OpenCV` |
| **Transcripción de Voz (Speech-to-Text)** | `Whisper` (Futuro) |
| **Análisis de Emoción Vocal** | `pyAudioAnalysis`, `opensmile` (Futuro) |

#### Frontend (Interfaz de Usuario)

| Rol | Herramienta |
| :--- | :--- |
| **Framework para Prototipado Web** | Streamlit |

#### Almacenamiento de Datos

| Rol | Herramienta |
| :--- | :--- |
| **Base de Datos Local Embebida** | SQLite |

#### Infraestructura y Despliegue

| Rol | Herramienta |
| :--- | :--- |
| **Entorno de Ejecución** | PC Local (sin servicios en la nube para el MVP) |
| **Túnel para Demos Públicas** | `ngrok` |
| **Control de Versiones / Repositorio** | GitHub |

---

### **4. Flujo de Datos del Sistema**

1.  **Entrada de Usuario:**
    *   **Video:** La webcam captura el rostro del usuario.
    *   **Voz:** El micrófono graba la voz del usuario.

2.  **Preprocesamiento:**
    *   La voz se transcribe a texto con una librería como `Whisper`.
    *   Las emociones faciales se detectan desde el video (`"triste"`).
    *   Las características de la voz se analizan para detectar la emoción (`"tono bajo"`).
    *   Toda esta información se empaqueta en un objeto estructurado.
        ```json
        {
          "text": "Últimamente me siento muy cansado...",
          "face_emotion": "sad",
          "voice_emotion": "low_energy"
        }
        ```

3.  **Procesamiento con IA (LM Studio):**
    *   El objeto preprocesado se formatea en un prompt y se envía a la API local de LM Studio.
    *   Ejemplo de prompt: `System: Eres un asistente empático. User: (emotion: sad, energy: low) Últimamente me siento muy cansado...`

4.  **Salida y Respuesta:**
    *   LM Studio devuelve una respuesta de texto generada por Mistral 7B.
    *   Opcionalmente, la respuesta se convierte a voz (Text-to-Speech) usando librerías como `Coqui TTS` o `ElevenLabs`.

---

### **5. Features Adicionales y Mejoras Planeadas**

*   **Speech Timeout Personalizable:**
    *   **Problema a resolver:** La IA podría interrumpir al usuario si este hace pausas largas al hablar.
    *   **Solución:** Implementar un temporizador de silencio ajustable. Si la IA interrumpe, se mostrará un mensaje preguntando al usuario si desea extender el tiempo de espera o desactivarlo.
    *   **Modo Manual:** Si se desactiva el temporizador, aparecerá un botón "Enviar" para que el usuario tenga control total sobre cuándo la IA debe escuchar y responder.

---

### **6. Estrategia de Recolección de Datos (Para Entrenamiento Futuro)**

*   **Objetivo:** Recopilar datos estructurados para, en el futuro, entrenar o afinar un modelo propio de empatía y detección emocional.
*   **Datos a Almacenar:**
    *   **NO** se guardará video ni audio en bruto para proteger la privacidad y ahorrar recursos.
    *   **SÍ** se guardarán metadatos procesados: emoción facial detectada, emoción vocal, tono, ritmo del habla, duración de silencios y la transcripción de texto.
*   **Formato de Almacenamiento:**
    *   Se utilizará una base de datos **SQLite** local. Cada interacción se guardará como un registro único con timestamp.
    *   **Ejemplo de Registro:**
        ```json
        {
          "timestamp": "2025-08-25T20:05:13Z",
          "text": "Me siento muy solo últimamente",
          "emotion_facial": "triste",
          "emotion_vocal": "triste",
          "tono": "bajo",
          "ritmo": "lento",
          "silencio_prev": "2.1s"
        }
        ```
*   **Impacto en Rendimiento:** Mínimo, ya que solo se almacenan datos de texto ligeros.

---

### **7. Guía de Instalación y Ejecución (Demo Actual)**

*   **Instalación:**
    1.  `pip install -r requirements.txt`

*   **Ejecución Local:**
    1.  `streamlit run app.py --server.address 0.0.0.0 --server.port 8501`
    2.  Acceder en el navegador: `http://localhost:8501`

*   **Exponer a la Web (para compartir demos):**
    1.  Instalar ngrok: `winget install ngrok -s msstore`
    2.  Registrarse en ngrok y obtener el authtoken.
    3.  Configurar el token: `ngrok config add-authtoken <TU_TOKEN>`
    4.  Ejecutar: `ngrok http 8501` (esto generará un enlace público).