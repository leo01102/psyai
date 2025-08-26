# PsyAI: Un Psicólogo con IA Emocional

[![Estado del Proyecto](https://img.shields.io/badge/estado-en%20desarrollo-green.svg)](https://github.com/tu-usuario/psyai)
[![Licencia](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE.md)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

**PsyAI es un prototipo de asistente psicológico que utiliza inteligencia artificial para ofrecer un apoyo más empático mediante la detección de emociones faciales y vocales del usuario en tiempo real.**

A diferencia de los chatbots tradicionales, PsyAI integra un análisis emocional multimodal para comprender el estado del usuario y adaptar sus respuestas, buscando cubrir una necesidad clave en el campo de la salud mental accesible.

<br>

![GIF o Screenshot de la aplicación en funcionamiento](docs/images/placeholder.png)
_(Reemplazar con una captura de pantalla o GIF de la demo)_

---

## ✨ Características Principales

- **Detección de Emociones Faciales:** Utiliza la webcam para identificar en tiempo real emociones básicas como alegría, tristeza, enojo y sorpresa.
- **IA Conversacional Local:** Se integra con un modelo de lenguaje (Mistral 7B) corriendo localmente a través de LM Studio para garantizar la privacidad.
- **Respuestas Empáticas:** El sistema utiliza el contexto emocional detectado para generar respuestas más consideradas y relevantes.
- **Interfaz Sencilla:** Construido con Streamlit para una experiencia de usuario limpia y directa.

---

## 🛠️ Stack Tecnológico

| Área                | Herramienta                                              |
| :------------------ | :------------------------------------------------------- |
| **IA & Backend**    | Python, LM Studio (Mistral 7B), `fer`/`deepface`, OpenCV |
| **Frontend**        | Streamlit                                                |
| **Base de Datos**   | SQLite                                                   |
| **Infraestructura** | Ejecución 100% Local                                     |

Para una descripción detallada de la arquitectura, consulta el [**Documento de Información del Proyecto**](docs/01_project_info.md).

---

## 🚀 Cómo Empezar

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

### Prerrequisitos

- **Python 3.9 o superior.**
- **Git** para clonar el repositorio.
- **LM Studio:** Descárgalo desde [lmstudio.ai](https://lmstudio.ai/).

### 1. Configuración del Modelo de IA (LM Studio)

Antes de ejecutar la aplicación, necesitas tener el modelo de lenguaje sirviendo localmente.

1.  Abre LM Studio.
2.  Busca y descarga el modelo `Mistral 7B Instruct`.
3.  Ve a la pestaña del servidor local (`<>`) y selecciona el modelo que descargaste.
4.  Haz clic en **"Start Server"**. Esto expondrá el modelo en una API local, generalmente en `http://localhost:1234/v1`.

### 2. Instalación del Proyecto

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/psyai.git
cd psyai

# 2. Crea y activa un entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instala las dependencias
pip install -r requirements.txt
```

### 3. Ejecución

Con el servidor de LM Studio corriendo en segundo plano, lanza la aplicación Streamlit:

```bash
streamlit run main.py
```

Abre tu navegador y ve a **http://localhost:8501**.

---

## 📂 Estructura del Proyecto

El proyecto sigue una estructura modular para facilitar el mantenimiento y la escalabilidad. El código fuente principal reside en la carpeta `src/`, separado por responsabilidades como el análisis de emociones, la interacción con el chat y la gestión de la base de datos.

➡️ Para una explicación detallada de cada carpeta y archivo, consulta la [**Guía de Estructura del Repositorio**](docs/02_structure_info.md).

➡️ Para entender cómo se almacenan los datos de las interacciones, revisa el [**Diseño de la Base de Datos**](docs/03_database_info.md).

---

## 🗺️ Roadmap y Futuras Mejoras

Tenemos varias mejoras planeadas para hacer de PsyAI una herramienta aún más robusta:

- [ ] **Análisis de Emoción Vocal:** Integrar librerías para detectar emociones a partir del tono y el ritmo de la voz.
- [ ] **Transcripción de Voz a Texto:** Utilizar `Whisper` para permitir al usuario hablar directamente con la aplicación.
- [ ] **Speech Timeout Personalizable:** Añadir una opción para que el usuario pueda hablar sin ser interrumpido.
- [ ] **Persistencia de Sesiones:** Mejorar el historial de conversaciones utilizando la base de datos SQLite.

---

## 🤝 Contribuciones

Este es un proyecto en crecimiento y las ideas son bienvenidas. Si deseas contribuir, por favor sigue el flujo de trabajo estándar:

1.  Crea un **Fork** del repositorio.
2.  Crea una nueva **rama** para tu feature (`git checkout -b feat/nombre-feature`).
3.  Haz **commit** de tus cambios.
4.  Abre un **Pull Request** hacia la rama `main` de este repositorio.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE.md](LICENSE.md) para más detalles.
