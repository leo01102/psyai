# backend/experiments/test_fer.py

from fer import FER
import cv2

# Captura de prueba desde cámara
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()

if ret:
    detector = FER(mtcnn=True)
    result = detector.top_emotion(frame)
    print("Resultado de detección:", result)
else:
    print("No se pudo capturar imagen de la cámara")
