### Estructura del Repositorio

```plaintext
psyai/
│
├── .gitignore          # Ignora archivos y carpetas que no deben subirse (ej: __pycache__, .env)
├── README.md           # Documentación principal del proyecto: qué es, cómo instalarlo y ejecutarlo.
├── requirements.txt    # Lista de dependencias de Python para instalar con pip.
├── config.py           # Archivo de configuración (ej: URL de la API de LM Studio, timeouts).
│
├── main.py             # Punto de entrada principal para lanzar la aplicación Streamlit.
│
├── src/                # Directorio principal para todo el código fuente de la aplicación.
│   │
│   ├── __init__.py     # Convierte 'src' en un paquete de Python.
│   │
│   ├── analysis/       # Módulo para el análisis de emociones (facial y de voz).
│   │   ├── __init__.py
│   │   ├── facial_emotion.py   # Lógica para detectar emociones faciales (reemplaza emotion_detector.py).
│   │   └── voice_emotion.py    # Lógica para analizar emociones vocales (futuro).
│   │
│   ├── chat/           # Módulo para la interacción con el modelo de lenguaje.
│   │   ├── __init__.py
│   │   └── llm_client.py       # Cliente para comunicarse con la API de LM Studio.
│   │   └── prompt_builder.py   # Lógica para construir los prompts con contexto emocional.
│   │
│   ├── database/       # Módulo para la gestión de la base de datos.
│   │   ├── __init__.py
│   │   └── data_manager.py     # Funciones para inicializar la DB, guardar y consultar registros.
│   │
│   └── ui/             # Módulo para los componentes de la interfaz de Streamlit.
│       ├── __init__.py
│       └── components.py       # Funciones que renderizan partes de la UI (ej: el video, el chat).
│
├── data/               # Directorio para los datos persistentes (no subir a Git si son sensibles).
│   └── interactions.db # El archivo de la base de datos SQLite.
│
└── notebooks/          # Jupyter notebooks para experimentación, análisis y pruebas.
    ├── 01_test_facial_recognition.ipynb
    └── 02_explore_voice_analysis.ipynb
```

---

### Descripción de Cada Componente

- **`.gitignore`**: Esencial para mantener el repositorio limpio. Debería incluir `__pycache__/`, `*.db`, `.env`, y cualquier otro archivo local.
- **`README.md`**: Tu carta de presentación. Incluirá la misión del proyecto, el stack tecnológico y las guías de instalación y uso.
- **`requirements.txt`**: Define las librerías necesarias. Centraliza la gestión de dependencias.
- **`config.py`**: Centraliza todas las variables de configuración. Facilita cambiar parámetros sin tener que buscar en todo el código. Por ejemplo, la URL de la API de LM Studio o el `speech_timeout` por defecto.
- **`main.py`**: Este es el nuevo `app.py`. Es el archivo que ejecutarás con `streamlit run main.py`. Su rol principal es orquestar la aplicación: inicializar la UI, llamar a los módulos de análisis y gestionar el flujo principal.
- **`src/`**: El corazón de tu aplicación.
  - **`analysis/`**: Separa la lógica de análisis. `facial_emotion.py` contendrá las funciones que ya tenías en `emotion_detector.py`. Cuando agregues el análisis de voz, su lógica irá en `voice_emotion.py`, manteniendo todo ordenado.
  - **`chat/`**: Dedicado a la comunicación con el LLM. `llm_client.py` se encargará de hacer las peticiones a LM Studio. `prompt_builder.py` será clave para formatear el texto del usuario junto con los datos emocionales (`"emotion: sad"`) antes de enviarlo.
  - **`database/`**: Responsable de la persistencia de datos. `data_manager.py` tendrá funciones como `create_connection()`, `save_interaction()` y `get_interactions()`.
  - **`ui/`**: Si tu interfaz crece, puedes mover funciones que dibujan elementos de Streamlit aquí para no saturar `main.py`.
- **`data/`**: Donde vivirá tu base de datos SQLite. Es buena práctica añadir `data/*.db` al `.gitignore` para no subir los datos de las interacciones al repositorio público.
- **`notebooks/`**: Un espacio fundamental para la experimentación. Antes de integrar una nueva librería (como `pyAudioAnalysis`), puedes probarla aquí de forma aislada.
