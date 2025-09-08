# src/analysis/voice_emotion.py | Lógica para analizar emociones vocales con Wav2Vec2.0

import torch
import librosa
import numpy as np
import os
import onnxruntime as ort
from abc import ABC, abstractmethod
from transformers import Wav2Vec2FeatureExtractor, AutoConfig
import io  # <--- NUEVO: para manejo de bytes en memoria
import soundfile as sf # <--- NUEVO: para leer los bytes

# --- CONFIGURACIÓN ---
MODEL_NAME = "superb/wav2vec2-base-superb-er"
MODELS_BASE_DIR = os.path.join("ai_resources", "models", "voice_emotion")

class BaseEmotionRecognizer(ABC):
    """Clase base abstracta para los reconocedores de emociones vocales."""
    def __init__(self, model_name: str, **kwargs):
        print(f"Inicializando procesador de características para '{model_name}'...")
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
        config = AutoConfig.from_pretrained(model_name)
        self.id2label = config.id2label
        self.target_sampling_rate = self.feature_extractor.sampling_rate

    @abstractmethod
    def _predict_logits(self, processed_audio: np.ndarray):
        """Método abstracto para la inferencia, implementado por las subclases."""
        pass

    def _preprocess_audio(self, audio_bytes: bytes):
        """
        Preprocesa audio desde bytes en memoria sin escribir en disco.
        """
        audio_buffer = io.BytesIO(audio_bytes)
        speech_array, samplerate = sf.read(audio_buffer)
        
        if samplerate != self.target_sampling_rate:
            speech_array = librosa.resample(y=speech_array, orig_sr=samplerate, target_sr=self.target_sampling_rate)
            
        return speech_array

    def predict(self, audio_bytes: bytes, chunk_length_s: float = 10.0):
        """
        Realiza la predicción de emociones a partir de datos de audio en bytes.
        """
        processed_audio = self._preprocess_audio(audio_bytes)
        
        if len(processed_audio) <= int(chunk_length_s * self.target_sampling_rate):
            all_logits = self._predict_logits(processed_audio)
        else:
            print(f"Audio largo detectado. Procesando en segmentos de {chunk_length_s}s...")
            chunk_size = int(chunk_length_s * self.target_sampling_rate)
            num_chunks = int(np.ceil(len(processed_audio) / chunk_size))
            
            chunk_logits = [self._predict_logits(processed_audio[i*chunk_size:(i+1)*chunk_size]) for i in range(num_chunks)]
            all_logits = np.mean(np.array(chunk_logits), axis=0)

        scores = torch.nn.functional.softmax(torch.from_numpy(all_logits), dim=1).numpy()[0]
        
        predictions = sorted(
            [{"label": self.id2label[i].upper(), "score": float(score)} for i, score in enumerate(scores)],
            key=lambda x: x["score"],
            reverse=True
        )
        return predictions

class ONNXEmotionRecognizer(BaseEmotionRecognizer):
    """Reconocedor usando un modelo ONNX optimizado."""
    def __init__(self, model_name: str, onnx_path: str, **kwargs):
        super().__init__(model_name)
        print(f"Cargando sesión de inferencia de ONNX Runtime desde '{onnx_path}'...")
        if not os.path.exists(onnx_path):
             raise FileNotFoundError(f"El modelo ONNX no fue encontrado en '{onnx_path}'. "
                                   f"Por favor, ejecuta el script 'scripts/export_to_onnx.py' y verifica la estructura de carpetas 'ai_resources/'.")
        self.session = ort.InferenceSession(onnx_path)
        self.input_name = self.session.get_inputs()[0].name
        print("¡Sesión ONNX cargada!")

    def _predict_logits(self, chunk: np.ndarray):
        inputs = self.feature_extractor(chunk, sampling_rate=self.target_sampling_rate, return_tensors="np", padding=True)
        onnx_inputs = {self.input_name: inputs.input_values.astype(np.float32)}
        logits = self.session.run(None, onnx_inputs)[0]
        return logits

def get_recognizer(method: str = "onnx_fp32", model_name: str = MODEL_NAME, onnx_dir: str = MODELS_BASE_DIR):
    """
    Función de fábrica que devuelve el tipo correcto de reconocedor según el método.
    """
    print("-" * 20)
    print(f"Cargando modelo de emoción vocal (Método: {method})")
    print("-" * 20)

    if method == "onnx_dynamic": 
        onnx_path = os.path.join(onnx_dir, "model_quant_dynamic.onnx")
        return ONNXEmotionRecognizer(model_name, onnx_path=onnx_path)
        
    elif method == "onnx_static":
        onnx_path = os.path.join(onnx_dir, "model_quant_static.onnx")
        return ONNXEmotionRecognizer(model_name, onnx_path=onnx_path)
        
    elif method == "onnx_fp32":
        onnx_path = os.path.join(onnx_dir, "model_float32.onnx")
        return ONNXEmotionRecognizer(model_name, onnx_path=onnx_path)
        
    else:
        raise ValueError(f"Método desconocido o no soportado en la aplicación: {method}")