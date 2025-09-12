# backend/src/analysis/facial_emotion.py | Lógica para detectar emociones faciales (reemplaza emotion_detector.py)

"""
Módulo especializado en el análisis de emociones faciales.
Utiliza la librería FER para detectar la emoción dominante y las puntuaciones
de un fotograma de video proporcionado.
"""

import logging

try:
    from fer import FER
except ImportError:
    print("Por favor, instala la librería 'fer' con: pip install fer")
    FER = None

def initialize_detector():
    """
    Inicializa y devuelve el detector de emociones faciales.
    """
    if FER is None:
        return None
    
    print("Cargando modelo de detección facial (FER)...")
    detector = FER(mtcnn=True)
    print("Modelo cargado exitosamente.")
    return detector

def analyze_frame_emotions(detector, frame_np):
    """
    Analiza un único fotograma de video y devuelve un diccionario de emociones.
    """
    if detector is None:
        raise RuntimeError("El detector FER no está inicializado. Asegúrate de que la librería 'fer' esté instalada.")

    try:
        detections = detector.detect_emotions(frame_np)
        
        if not detections:
            return None
            
        first_face = detections[0]
        emotions = first_face["emotions"]
        dominant_emotion = max(emotions, key=emotions.get)
        
        return {
            "dominant_emotion": dominant_emotion,
            "scores": emotions,
            "bounding_box": first_face["box"]
        }
    except Exception as e:
        # --- BLOQUE CORREGIDO ---
        # En lugar de un print, usamos el logger.
        # Esto es un error no crítico y recuperable, por lo que un 'warning' es apropiado.
        logging.warning(f"Error interno no crítico en la librería FER: {e}. Esto es a menudo recuperable.")
        return None
