# main.py | Punto de entrada principal para lanzar la aplicación Streamlit

import streamlit as st
from PIL import Image
from src.analysis.facial_emotion import analyze_image

st.set_page_config(page_title="PsyAI - Demo", layout="centered")
st.title("PsyAI - Demo")
st.write("Toma una foto con la cámara y el modelo detectará la emoción dominante.")

img_file = st.camera_input("Toma una foto (si tu navegador lo permite)")

if img_file is not None:
    img = Image.open(img_file)
    st.image(img, caption="Foto tomada", use_container_width=True)
    with st.spinner("Analizando..."):
        try:
            result = analyze_image(img)
            st.success(f"Emoción detectada: **{result['dominant']}** (backend: {result['backend']})")
            st.write("Puntajes:")
            st.json(result['scores'])
            # Opcional: respuesta empática simple
            empathic = {
                "happy": "¡Me alegra verlo! ¿Querés contarme qué te puso así?",
                "sad": "Siento que te sientas triste. ¿Querés hablar de eso?",
                "angry": "Parece que estás enojado. Respiremos un momento.",
                "surprise": "Vaya, te sorprendió algo. ¿Qué sucedió?",
                "neutral": "Estás con un ánimo neutro. ¿Querés seguir charlando?",
            }
            key = result['dominant'].lower()
            st.info(empathic.get(key, "Gracias por compartir cómo te sentís."))
        except Exception as e:
            st.error("No se pudo analizar la imagen: " + str(e))