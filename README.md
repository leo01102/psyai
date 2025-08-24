# psyai

Demo MVP: detector de emociones por cámara usando Streamlit + DeepFace/FER.

## Setup (Windows)

# 1. Crear un entorno nuevo llamado psyai
conda create -n psyai python=3.10 -y

# 2. Activar el entorno
conda activate psyai

# 3. Instalar dependencias desde requirements.txt
pip install -r requirements.txt

# 4. Correr el servidor Streamlit
streamlit run app.py

## Uso

- Permitir cámara en el navegador.
- Click en "Take photo" / "Tomar foto".
