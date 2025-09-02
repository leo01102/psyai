### **1. Información General del Proyecto**

- **Nombre del Proyecto:** PsyAI - Asistente con IA Emocional
- **Misión:** Desarrollar un asistente de IA que ofrezca un apoyo empático mediante la detección de emociones faciales y la interacción por voz en tiempo real, recordando interacciones pasadas para un contexto más profundo.
- **Tecnología Principal de IA:** Se utiliza el modelo de lenguaje `Llama 3.1 8B` a través de la API de `Groq`.
- **Propuesta de Valor:** A diferencia de los chatbots sin estado, PsyAI integra análisis emocional multimodal, un ciclo de voz completo y una memoria persistente y cifrada para crear una experiencia de usuario más segura, humana y conectada.

---

### **2. Estado Actual del Prototipo**

- **Detección de Emociones Faciales:** Un modelo (`fer`) identifica un estado emocional estable a partir del stream de la webcam.
- **Ciclo de Audio Completo:** Se ha implementado un flujo de conversación por voz de principio a fin:
  - **Captura de Voz:** El usuario graba su voz (`audiorecorder`).
  - **Transcripción a Texto (STT):** La voz se transcribe usando la API de **Deepgram**.
  - **Síntesis de Voz (TTS):** La respuesta del LLM se convierte a audio usando **Edge-TTS**.
- **Memoria a Largo Plazo:** La IA extrae y guarda hechos clave de la conversación (ej. nombre, temas recurrentes) en una base de datos local para usarlos en prompts futuros.
- **Persistencia y Seguridad:** Todas las interacciones y los datos de memoria se guardan en una base de datos **SQLite**, con los campos de texto **cifrados** para proteger la privacidad.
- **Respuesta Empática:** El bot utiliza el historial del chat, la memoria a largo plazo y la emoción facial detectada para generar respuestas contextuales a través de **Groq**.

---

### **3. Arquitectura y Stack Tecnológico**

#### Backend y Lógica de IA

| Rol                                 | Herramienta                 |
| :---------------------------------- | :-------------------------- |
| **Lenguaje y Entorno de Ejecución** | Python                      |
| **IA Conversacional (LLM)**         | **Groq API** (Llama 3.1 8B) |
| **Detección de Emoción Facial**     | `fer` (con TensorFlow)      |
| **Transcripción de Voz (STT)**      | **Deepgram API**            |
| **Síntesis de Voz (TTS)**           | **Edge-TTS**                |
| **Seguridad de Datos**              | `cryptography` (AES-GCM)    |

#### Frontend (Interfaz de Usuario)

| Rol                      | Herramienta        |
| :----------------------- | :----------------- |
| **Framework Web**        | Streamlit          |
| **Video en Tiempo Real** | `streamlit-webrtc` |
| **Captura de Audio**     | `audiorecorder`    |

#### Almacenamiento y Pruebas

| Rol                      | Herramienta |
| :----------------------- | :---------- |
| **Base de Datos Local**  | SQLite      |
| **Framework de Pruebas** | `pytest`    |

---

### **4. Flujo de Datos del Sistema**

1.  **Entrada de Usuario:** El usuario graba su voz. Mientras tanto, el stream de la webcam es analizado continuamente para mantener un estado emocional agregado.
2.  **Transcripción:** El audio se envía a la API de **Deepgram** y se recibe el texto.
3.  **Construcción del Prompt:** El texto transcrito, el historial de chat, la memoria a largo plazo (desde SQLite) y el estado emocional facial actual se combinan en un prompt estructurado.
4.  **Procesamiento con LLM:** El prompt se envía a la **API de Groq**. Llama 3.1 genera una respuesta de texto.
5.  **Extracción de Memoria:** La conversación (pregunta del usuario y respuesta de la IA) se envía de nuevo a Groq con un prompt específico para extraer hechos clave en formato JSON.
6.  **Persistencia:** La interacción del usuario y la IA, junto con los nuevos hechos de memoria, se cifran y se guardan en la base de datos **SQLite**.
7.  **Salida de Audio:** La respuesta de la IA se convierte a audio mediante **Edge-TTS** y se reproduce automáticamente.
