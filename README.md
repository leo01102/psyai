# PsyAI: Un Asistente con IA Emocional

[![Estado del Proyecto](https://img.shields.io/badge/estado-en%20desarrollo-green.svg)](https://github.com/leo01102/psyai)
[![Licencia](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

**PsyAI es un prototipo de asistente de IA que ofrece un apoyo empático mediante la detección de emociones faciales y la interacción por voz en tiempo real.**

A diferencia de los chatbots tradicionales, PsyAI integra un análisis emocional multimodal y una memoria persistente para comprender el estado del usuario y adaptar sus respuestas, buscando crear una experiencia más humana y conectada.

<br>

<!-- ![GIF de la aplicación en funcionamiento](docs/images/demo.gif) -->

_(Reemplazar con una captura de pantalla o GIF de la demo)_

---

## ✨ Características Principales

- **Detección de Emociones Faciales:** Utiliza la webcam para identificar en tiempo real un estado emocional estable y agregado.
- **Interacción por Voz Completa:** Conversa de forma natural con la IA gracias a un ciclo de audio completo:
  - **Transcripción Rápida:** Utiliza **Deepgram** para una transcripción precisa de la voz del usuario.
  - **Respuestas Habladas:** Genera audio con una voz natural usando **Edge-TTS**.
- **IA Conversacional de Alta Velocidad:** Se integra con el modelo **Llama 3.1** a través de la API de **Groq** para obtener respuestas casi instantáneas.
- **Memoria a Largo Plazo:** La IA recuerda datos clave de conversaciones anteriores para ofrecer una experiencia más personalizada.
- **Seguridad y Privacidad:** Las conversaciones y los datos de memoria se cifran antes de guardarse en la base de datos local.

---

## 🛠️ Stack Tecnológico

| Área              | Herramienta                                                                     |
| :---------------- | :------------------------------------------------------------------------------ |
| **IA & Backend**  | Python, **Groq (Llama 3.1)**, **Deepgram**, **Edge-TTS**, `fer`, `cryptography` |
| **Frontend**      | Streamlit, `audiorecorder`, `streamlit-webrtc`                                  |
| **Base de Datos** | SQLite                                                                          |
| **Testing**       | `pytest`                                                                        |

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

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. (Opcional) Puebla la base de datos con datos de prueba
python scripts/seed_database.py
```

### 2. Configuración de Claves (¡Importante!)

#### Paso A: Generar Clave de Cifrado

La aplicación necesita una clave secreta para cifrar los datos en la base de datos. Ejecuta el siguiente script para generar una:

```bash
python scripts/generate_key.py
```

Copia la línea `ENCRYPTION_KEY=...` que se mostrará en la terminal.

#### Paso B: Crear el Archivo `.env`

1.  En la raíz del proyecto, crea un archivo llamado `.env`.
2.  Pega el siguiente contenido, reemplazando los valores con tus propias claves y la clave de cifrado que acabas de generar:

    ```env
    # .env
    DEEPGRAM_API_KEY="TU_API_KEY_DE_DEEPGRAM"
    GROQ_API_KEY="TU_API_KEY_DE_GROQ"
    ENCRYPTION_KEY="PEGA_AQUI_LA_CLAVE_GENERADA"
    ```

### 3. Ejecución

Con el archivo `.env` configurado, lanza la aplicación Streamlit:

```bash
streamlit run main.py
```

Abre tu navegador y ve a **http://localhost:8501**.

---

## 📂 Estructura del Proyecto

El proyecto sigue una estructura modular profesional, separando la lógica, las pruebas y los scripts de utilidad.

➡️ Para una explicación detallada de cada carpeta y archivo, consulta la [**Guía de Estructura del Repositorio**](docs/02_structure_info.md).

---

## 🗺️ Roadmap y Futuras Mejoras

- [x] **Ciclo de Audio Completo (STT/TTS)**
- [x] **Análisis de Emoción Facial**
- [x] **Persistencia de Sesiones y Memoria (Cifrada)**
- [x] **Estructura de UI Modular**
- [ ] **Análisis de Emoción Vocal:** Integrar librerías para detectar emociones a partir del tono y el ritmo de la voz.
- [ ] **Interfaz de Usuario Avanzada:** Implementar un botón "hold-to-talk", timeline de emociones y opciones de speech-timeout.

---

## 🤝 Contribuciones

Este es un proyecto en crecimiento y las ideas son bienvenidas. Por favor, sigue el flujo de trabajo estándar de Fork y Pull Request.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
