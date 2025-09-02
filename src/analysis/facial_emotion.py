# src/analysis/facial_emotion.py | Lógica para detectar emociones faciales (reemplaza emotion_detector.py)

"""
Módulo especializado en el análisis de emociones faciales.
Utiliza la librería FER para detectar la emoción dominante y las puntuaciones
de un fotograma de video proporcionado.
"""

# Importamos las librerías necesarias. El try/except es una buena práctica
# para dar un mensaje de error claro si la librería no está instalada.
try:
    from fer import FER
except ImportError:
    print("Por favor, instala la librería 'fer' con: pip install fer")
    FER = None

def initialize_detector():
    """
    Inicializa y devuelve el detector de emociones faciales.
    Esta función se debe llamar UNA SOLA VEZ al inicio de la aplicación
    para evitar cargar el modelo repetidamente.
    
    Returns:
        Un objeto detector de FER si la librería está disponible, si no, None.
    """
    if FER is None:
        return None
    
    # mtcnn=True utiliza un detector de caras más avanzado y preciso.
    print("Cargando modelo de detección facial (FER)...")
    detector = FER(mtcnn=True)
    print("Modelo cargado exitosamente.")
    return detector

def analyze_frame_emotions(detector, frame_np):
    """
    Analiza un único fotograma de video y devuelve un diccionario de emociones.
    
    Args:
        detector: El objeto FER pre-inicializado por initialize_detector().
        frame_np: Un fotograma de video como un array de NumPy (en formato BGR).
        
    Returns:
        Un diccionario con los resultados del análisis o None si no se detecta cara.
        Ejemplo de retorno: {'dominant_emotion': 'happy', 'scores': {'happy': 0.9, ...}}
    """
    if detector is None:
        raise RuntimeError("El detector FER no está inicializado. Asegúrate de que la librería 'fer' esté instalada.")

    try:
        # La librería FER se encarga de la detección de la cara y el análisis de emociones.
        # El resultado es una lista de caras detectadas.
        detections = detector.detect_emotions(frame_np)
        
        if not detections:
            return None  # No se detectó ninguna cara en el fotograma.
            
        # Nos enfocamos en la primera cara detectada para este prototipo.
        first_face = detections[0]
        emotions = first_face["emotions"]
        dominant_emotion = max(emotions, key=emotions.get)
        
        # Devolvemos un payload estructurado y limpio.
        return {
            "dominant_emotion": dominant_emotion,
            "scores": emotions,
            "bounding_box": first_face["box"]  # Coordenadas (x, y, w, h) para dibujar
        }
    except Exception as e:
        # Es bueno registrar el error para depuración, pero no debe detener la aplicación.
        print(f"Error durante el análisis facial: {e}")
        return None