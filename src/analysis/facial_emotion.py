# src/analysis/facial_emotion.py | Lógica para detectar emociones faciales (reemplaza emotion_detector.py)

import numpy as np
import cv2
from PIL import Image

# Intentaremos usar FER si está instalado; si no, haremos fallback con Haar cascades (OpenCV puro).
try:
    from fer import FER
    FER_AVAILABLE = True
except Exception:
    FER_AVAILABLE = False

def analyze_with_fer(img_np):
    """
    img_np: numpy array (RGB)
    returns: dict {'dominant': str, 'scores': {...}}
    """
    if not FER_AVAILABLE:
        raise ImportError("FER no está disponible")
    detector = FER(mtcnn=True)
    detections = detector.detect_emotions(img_np)
    if not detections:
        raise ValueError("No se detectó ninguna cara (FER).")
    emotions = detections[0]["emotions"]
    dominant = max(emotions, key=emotions.get)
    return {"dominant": dominant, "scores": emotions}

def analyze_with_haar(img_np):
    """
    Método de reserva usando OpenCV Haar cascades.
    Detecta cara + sonrisa y devuelve 'happy' o 'neutral' según un umbral simple.
    img_np: numpy array (RGB)
    """
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    if len(faces) == 0:
        raise ValueError("No se detectó ninguna cara (Haar fallback).")

    # tomamos la primera cara detectada
    (x, y, w, h) = faces[0]
    roi_gray = gray[y:y+h, x:x+w]

    # detect smiles dentro del ROI de la cara
    smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.7, minNeighbors=22, minSize=(25, 25))
    # heurística simple:
    if len(smiles) > 0:
        dominant = "happy"
        scores = {"happy": 0.9, "neutral": 0.1}
    else:
        dominant = "neutral"
        scores = {"happy": 0.05, "neutral": 0.95}

    return {"dominant": dominant, "scores": scores}

def analyze_image(img_pil):
    """
    img_pil: PIL.Image
    returns: {'dominant': str, 'scores': {...}, 'backend': 'fer'|'haar'}
    """
    img_np = np.array(img_pil.convert("RGB"))
    # First try FER if available
    if FER_AVAILABLE:
        try:
            out = analyze_with_fer(img_np)
            out["backend"] = "fer"
            return out
        except Exception as e:
            # log in console for debugging, but fallthrough to haar
            print(f"[emotion_detector] FER failed: {e}")

    # Haar fallback (no TF)
    out = analyze_with_haar(img_np)
    out["backend"] = "haar"
    return out