### Estructura del Repositorio

La estructura se ha diseñado para separar claramente el código fuente de la aplicación (`src`), los recursos de IA (`ai_resources`), los scripts de utilidad (`scripts`) y los datos persistentes (`data`).

```plaintext
psyai/
│
├── .env                # Archivo local para claves de API y cifrado (ignorado por Git).
├── .gitignore          # Ignora archivos y carpetas que no deben subirse.
├── README.md           # Documentación principal y guía de inicio rápido.
├── requirements.txt    # Dependencias de Python.
├── config.py           # Carga y centraliza las variables de configuración.
│
├── main.py             # Punto de entrada principal para la aplicación Streamlit.
│
├───ai_resources/       # (NUEVO) Almacena todos los recursos de IA locales.
│   ├── models/
│   │   └── voice_emotion/  # Modelos ONNX optimizados para emoción vocal.
│   └── calibration_data/ # (Ignorado por Git) Archivos .wav para calibración de ONNX.
│
├───data/               # (Ignorado por Git) Almacena la base de datos local.
│   └── psyai.db
│
├───docs/               # Documentación detallada del proyecto.
│
├───logs/               # (Ignorado por Git) Guarda los logs de ejecución.
│
├───scripts/            # Scripts de utilidad que no forman parte de la app principal.
│   ├── export_to_onnx.py # (NUEVO) Script para convertir el modelo de voz a ONNX.
│   └── generate_key.py   # Script para crear la clave de cifrado.
│
├───src/                # Código fuente de la aplicación.
│   ├── analysis/       # Módulos para analizar las entradas del usuario.
│   │   ├── facial_emotion.py      # Lógica de detección facial (FER).
│   │   ├── voice_emotion.py       # (NUEVO) Lógica de emoción vocal (Wav2Vec2/ONNX).
│   │   └── voice_transcription.py # (Refactorizado) Lógica de STT (Deepgram).
│   │
│   ├── audio/          # Módulo para la salida de audio (TTS).
│   ├── chat/           # Módulos para la interacción con el LLM (Groq, Prompts).
│   ├── database/       # Módulo para la gestión de la base de datos SQLite y cifrado.
│   ├── ui/             # Módulo para componentes reutilizables de Streamlit.
│   └── utils/          # Utilidades compartidas (logger).
│
└───tests/              # Pruebas automatizadas.
    └── ...
```

---

### Descripción de Cada Componente

-   **`ai_resources/`**: (NUEVO) Carpeta dedicada a los artefactos de IA que no son código Python.
    -   **`models/`**: Contiene los modelos pre-entrenados y optimizados (como los archivos `.onnx`) listos para inferencia.
    -   **`calibration_data/`**: Almacena datos de muestra (ej. archivos `.wav`) utilizados por scripts para optimizar o cuantizar modelos.
-   **`scripts/`**: Hogar de scripts de utilidad.
    -   `generate_key.py`: Se usa una vez para crear la `ENCRYPTION_KEY`.
    -   `export_to_onnx.py`: Se usa una vez para descargar y convertir el modelo de emoción vocal de Hugging Face a un formato ONNX más rápido.
-   **`src/`**: El corazón de la aplicación.
    -   **`analysis/`**: (Refactorizado) Ahora tiene responsabilidades claras:
        -   `facial_emotion.py`: Extrae emociones del video.
        -   `voice_emotion.py`: Extrae emociones del audio (Wav2Vec 2.0).
        -   `voice_transcription.py`: Transcribe el audio a texto (Deepgram).
    -   **`database/`**: Gestiona la persistencia. `data_manager.py` define el esquema, maneja el cifrado y proporciona funciones CRUD para la base de datos.
-   **`main.py`**: Orquesta la aplicación, carga los modelos (facial y vocal), gestiona el estado de la sesión y coordina el flujo de datos multimodal.
