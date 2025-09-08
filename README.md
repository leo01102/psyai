# PsyAI: Un Asistente con IA Emocional Multimodal

[![Estado del Proyecto](https://img.shields.io/badge/estado-en%20desarrollo-green.svg)](https://github.com/leo01102/psyai)
[![Licencia](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

**PsyAI es un prototipo de asistente de IA que ofrece un apoyo empático mediante la detección de emociones faciales y vocales, combinado con una interacción por voz en tiempo real.**

A diferencia de los chatbots tradicionales, PsyAI integra un análisis emocional multimodal (rostro y voz) para comprender el estado completo del usuario y adaptar sus respuestas, buscando crear una experiencia de usuario más humana y conectada.

<br>

<!-- ![GIF de la aplicación en funcionamiento](docs/images/demo.gif) -->

_(Reemplazar con una captura de pantalla o GIF de la demo)_

---

## ✨ Características Principales

- **Análisis Emocional Multimodal:**
  - **Detección de Emociones Faciales:** Utiliza la webcam para identificar en tiempo real emociones (ej. alegría, tristeza, enojo) usando `fer`.
  - **Reconocimiento de Emociones Vocales:** Analiza el tono de voz para detectar la emoción subyacente (ej. calma, felicidad, rabia) usando un modelo **Wav2Vec 2.0** optimizado.
- **Interacción por Voz Completa:** Conversa de forma natural con la IA gracias a un ciclo de audio completo:
  - **Transcripción en Tiempo Real:** Utiliza **Deepgram** para una transcripción rápida y precisa de la voz del usuario.
  - **Respuestas Habladas:** Genera audio con una voz natural usando **Edge-TTS**.
- **IA Conversacional de Alta Velocidad:** Se integra con el modelo **Llama 3.1** a través de la API de **Groq** para obtener respuestas casi instantáneas.
- **Respuestas Empáticas Contextualizadas:** El sistema combina el texto del usuario con el contexto emocional multimodal (facial + vocal) para generar respuestas más consideradas y relevantes.
- **Memoria Persistente y Cifrada:** Recuerda hechos clave de conversaciones pasadas (ej. nombre, temas recurrentes) guardándolos de forma segura en una base de datos **SQLite** local con cifrado AES.

---

## 🛠️ Stack Tecnológico

| Área                | Herramienta                                                    |
| :------------------ | :------------------------------------------------------------- |
| **IA & Backend**    | Python, **Groq (Llama 3.1)**, **Deepgram (STT)**, **Edge-TTS** |
| **Análisis Facial** | `fer` (TensorFlow)                                             |
| **Análisis Vocal**  | `transformers`, `Wav2Vec 2.0`, `ONNX Runtime`, `librosa`       |
| **Frontend**        | Streamlit, `streamlit-webrtc`, `audiorecorder`                 |
| **Base de Datos**   | SQLite, `cryptography` (para cifrado)                          |
| **Infraestructura** | Ejecución Local (con APIs externas)                            |

Para una descripción detallada de la arquitectura, consulta el [**Documento de Información del Proyecto**](docs/01_project_info.md).

---

## 🚀 Cómo Empezar

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

### Prerrequisitos

- **Python 3.9–3.12.** Probado con **Python 3.11.9**.
- **Git** para clonar el repositorio.
- **Cuentas de API:**
  - Una cuenta en [**Groq**](https://console.groq.com/keys) para obtener una API Key.
  - Una cuenta en [**Deepgram**](https://console.deepgram.com/signup) para obtener una API Key.
- **(Opcional) Datos de Calibración:** Si deseas optimizar el modelo de voz (requiere mucha RAM), descarga algunos archivos `.wav` de habla (ej. de [RAVDESS](https://zenodo.org/record/1188976)).

### 1. Instalación del Proyecto

```bash
# 1. Clona el repositorio
git clone https://github.com/leo01102/psyai.git
cd psyai

# 2. Crea y activa un entorno virtual (recomendado)
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
# source .venv/bin/activate

# 3. Instala todas las dependencias
pip install -r requirements.txt
```

### 2. Configuración de API Keys y Cifrado

1.  En la raíz del proyecto, crea un archivo llamado `.env`.
2.  Ejecuta el script para generar tu clave de cifrado local:
    ```bash
    python scripts/generate_key.py
    ```
3.  Copia la clave generada (`ENCRYPTION_KEY=...`) y pégala en tu archivo `.env`.
4.  Añade tus claves de API al mismo archivo `.env`:

    ```env
    # .env
    DEEPGRAM_API_KEY="TU_API_KEY_DE_DEEPGRAM"
    GROQ_API_KEY="TU_API_KEY_DE_GROQ"
    ENCRYPTION_KEY="TU_CLAVE_GENERADA_EN_EL_PASO_ANTERIOR"
    ```

### 3. Generación de Modelos de IA Locales

Este proyecto utiliza una versión optimizada (ONNX) del modelo de emoción vocal. Debes generarla una sola vez ejecutando el siguiente script:

```bash
# Este script descargará el modelo de Hugging Face y lo convertirá
python scripts/export_to_onnx.py
```

- El script creará automáticamente los modelos `float32` y `dynamic_quant` en `ai_resources/models/voice_emotion/`.
- Te **preguntará** si deseas ejecutar la "cuantización estática". Este paso es **opcional** y consume mucha RAM. Puedes escribir `n` (No) y la aplicación funcionará perfectamente.

### 4. Ejecución

Con el archivo `.env` configurado y los modelos generados, lanza la aplicación:

```bash
streamlit run main.py
```

Abre tu navegador y ve a **http://localhost:8501**.

---

## 📂 Estructura del Proyecto

El proyecto sigue una estructura modular para facilitar el mantenimiento. El código fuente reside en `src/` y los modelos de IA en `ai_resources/`.

➡️ Para una explicación detallada de cada carpeta y archivo, consulta la [**Guía de Estructura del Repositorio**](docs/02_structure_info.md).

---

## 🗺️ Roadmap y Futuras Mejoras

- [x] **Transcripción de Voz a Texto:** Implementado con Deepgram.
- [x] **Análisis de Emoción Facial:** Integrado con `fer`.
- [x] **Análisis de Emoción Vocal:** ¡Implementado con Wav2Vec 2.0 y ONNX!
- [x] **Respuestas Multimodales:** El prompt de la IA ahora usa contexto facial y vocal.
- [x] **Persistencia y Memoria Cifrada:** Implementado con SQLite y `cryptography`.
- [x] **Ciclo de Audio Completo (TTS/STT):** Implementado.
- [x] **Mejorar Componentes UI:** Lógica de renderizado movida a `src/ui/components.py`.

---

## 🤝 Contribuciones

Este es un proyecto en crecimiento y las ideas son bienvenidas. Si deseas contribuir, por favor sigue el flujo de trabajo estándar de Fork y Pull Request.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
