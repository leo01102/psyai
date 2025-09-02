### Estructura del Repositorio

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
├───data/               # (Ignorado por Git) Almacena la base de datos local.
│   └── psyai.db
│
├───docs/               # Documentación detallada del proyecto.
│   ├── 01_project_info.md
│   ├── 02_structure_info.md
│   └── 03_database_info.md
│
├───logs/               # (Ignorado por Git) Guarda los logs de ejecución de la aplicación.
│   └── psyai.log
│
├───notebooks/          # Jupyter notebooks para experimentación.
│
├───scripts/            # Scripts de utilidad que no forman parte de la app principal.
│   └── generate_key.py
│
├───src/                # Código fuente de la aplicación.
│   ├── analysis/       # Módulos para analizar las entradas del usuario (cara, voz).
│   ├── audio/          # Módulo para la salida de audio (Text-to-Speech).
│   ├── chat/           # Módulos para la interacción con el LLM.
│   ├── database/       # Módulo para la gestión de la base de datos SQLite.
│   ├── ui/             # Módulo para componentes reutilizables de la interfaz.
│   └── utils/          # Utilidades compartidas, como la configuración del logger.
│
└───tests/              # Pruebas automatizadas.
    ├── fixtures/       # Archivos de datos para las pruebas (ej. audio de prueba).
    ├── integration/    # Pruebas que verifican la interacción entre varios módulos.
    └── unit/           # Pruebas que verifican un solo módulo de forma aislada.
```

---

### Descripción de Cada Componente

- **`.env`**: Almacena secretos como las API keys y la clave de cifrado. Es vital para la seguridad y no debe subirse a Git.
- **`config.py`**: El único punto de acceso a las variables de configuración, cargándolas de forma segura desde `.env`.
- **`main.py`**: Orquesta la aplicación, gestiona el estado de la sesión y coordina las llamadas a los diferentes módulos.
- **`scripts/`**: Hogar de scripts de utilidad, como `generate_key.py`, que ayudan en la configuración pero no son parte de la aplicación en sí.
- **`src/`**: El corazón de la aplicación.
  - **`analysis/`**: Interpreta las entradas del usuario. `facial_emotion.py` extrae emociones del video y `voice_emotion.py` transcribe el audio.
  - **`audio/`**: Gestiona la salida de audio. `tts_player.py` convierte el texto de la IA en voz.
  - **`chat/`**: Se comunica con el LLM. `llm_client.py` gestiona las llamadas a la API de Groq y `prompt_builder.py` formatea los prompts.
  - **`database/`**: Gestiona la persistencia. `data_manager.py` define el esquema, maneja el cifrado y proporciona funciones para interactuar con la base de datos.
  - **`ui/`**: Contiene funciones que renderizan componentes de la interfaz para mantener `main.py` limpio.
  - **`utils/`**: Código de utilidad compartido. `logger_config.py` centraliza la configuración del sistema de logging.
- **`tests/`**: Contiene pruebas automatizadas para garantizar la fiabilidad del código.
