# scripts/export_to_onnx.py

import torch
import os
import glob
import numpy as np
import librosa
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
from onnxruntime.quantization import quantize_dynamic, quantize_static, QuantType
from onnxruntime.quantization.calibrate import CalibrationDataReader
import warnings

# --- CONFIGURACIÓN ---
MODEL_NAME = "superb/wav2vec2-base-superb-er"
ONNX_MODELS_DIR = os.path.join("ai_resources", "models", "voice_emotion")
CALIBRATION_DATA_DIR = os.path.join("ai_resources", "calibration_data")
# ---------------------

# Ignorar warnings específicos de librosa que pueden aparecer
warnings.filterwarnings('ignore', category=FutureWarning, module='librosa')

class AudioCalibrationDataReader(CalibrationDataReader):
    """
    Lee archivos de audio de la carpeta de calibración y los prepara
    para que el cuantizador de ONNX pueda 'medir' los rangos de activación.
    """
    def __init__(self, data_dir: str, feature_extractor, num_files_to_use=20, num_segments_per_file=5, segment_length_s=3):
        self.feature_extractor = feature_extractor
        self.segment_length = int(segment_length_s * self.feature_extractor.sampling_rate)
        
        wav_files = glob.glob(os.path.join(data_dir, "*.wav"))
        if not wav_files:
            raise ValueError(f"No se encontraron archivos .wav en el directorio de calibración: '{data_dir}'. "
                             "Por favor, descarga algunos archivos de audio (ej. de CREMA-D o RAVDESS) y colócalos allí.")
        
        files_to_process = wav_files[:num_files_to_use]
        print(f"Usando {len(files_to_process)} de {len(wav_files)} archivos de audio de '{data_dir}' para calibración.")
        
        self.segments_list = []
        for file_path in files_to_process:
            try:
                speech, sr = librosa.load(file_path, sr=self.feature_extractor.sampling_rate)
                if len(speech) < self.segment_length:
                    continue
                
                for _ in range(num_segments_per_file):
                    start = np.random.randint(0, len(speech) - self.segment_length + 1)
                    segment = speech[start : start + self.segment_length]
                    self.segments_list.append(segment)
            except Exception as e:
                print(f"Advertencia: No se pudo procesar {os.path.basename(file_path)}. Error: {e}")

        print(f"Generados {len(self.segments_list)} segmentos de audio para una calibración robusta.")
        self.data_iter = iter(self.segments_list)

    def get_next(self):
        segment = next(self.data_iter, None)
        if segment is None:
            return None
        
        inputs = self.feature_extractor(
            segment, 
            sampling_rate=self.feature_extractor.sampling_rate, 
            return_tensors="np", 
            padding=True
        )
        return {"input_values": inputs.input_values.astype(np.float32)}

def export_models():
    """Función principal para exportar y cuantizar los modelos."""
    os.makedirs(ONNX_MODELS_DIR, exist_ok=True)
    os.makedirs(CALIBRATION_DATA_DIR, exist_ok=True)
    
    print("Cargando modelo base de PyTorch desde Hugging Face...")
    model = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_NAME)
    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_NAME)

    float32_path = os.path.join(ONNX_MODELS_DIR, "model_float32.onnx")
    
    if not os.path.exists(float32_path):
        print(f"\n1. Exportando modelo base a ONNX (Float32) en '{float32_path}'...")
        dummy_input = torch.randn(1, 16000)
        torch.onnx.export(
            model, dummy_input, float32_path,
            opset_version=14,
            input_names=["input_values"], output_names=["logits"],
            dynamic_axes={"input_values": {1: "sequence_length"}, "logits": {1: "sequence_length"}}
        )
        print("✅ Exportación a Float32 completada.")
    else:
        print(f"ℹ️ El modelo ONNX (Float32) '{float32_path}' ya existe. Saltando exportación.")

    dynamic_quant_path = os.path.join(ONNX_MODELS_DIR, "model_quant_dynamic.onnx")
    if not os.path.exists(dynamic_quant_path):
        print(f"\n2. Aplicando cuantización dinámica a '{dynamic_quant_path}'...")
        quantize_dynamic(
            model_input=float32_path,
            model_output=dynamic_quant_path,
            weight_type=QuantType.QInt8
        )
        print("✅ Cuantización dinámica completada.")
    else:
        print(f"ℹ️ El modelo cuantizado dinámicamente '{dynamic_quant_path}' ya existe. Saltando.")
        
    print("\n" + "="*50)
    print("PASO 3: CUANTIZACIÓN ESTÁTICA (OPCIONAL)")
    print("="*50)
    print("Este es el paso que MÁS MEMORIA RAM CONSUME y requiere archivos de audio en la carpeta 'calibration_data'.")
    print("Puede fallar si no tienes suficiente RAM (se recomiendan >8GB).")
    print("La aplicación principal funcionará correctamente sin este modelo, usando la versión 'float32'.")
    
    choice = input("¿Deseas intentar la cuantización estática? (s/n): ").lower().strip()

    if choice in ['s', 'si', 'y', 'yes']:
        print("\nIniciando cuantización estática...")
        static_quant_path = os.path.join(ONNX_MODELS_DIR, "model_quant_static.onnx")
        if not os.path.exists(static_quant_path):
            print(f"Aplicando cuantización estática con calibración a '{static_quant_path}'...")
            try:
                calibration_data_reader = AudioCalibrationDataReader(CALIBRATION_DATA_DIR, feature_extractor)
                quantize_static(
                    model_input=float32_path,
                    model_output=static_quant_path,
                    calibration_data_reader=calibration_data_reader,
                    quant_format='QDQ',
                    activation_type=QuantType.QInt8,
                    weight_type=QuantType.QInt8,
                )
                print("✅ Cuantización estática completada.")
            except ValueError as e:
                print(f"\n❌ ERROR durante la calibración estática: {e}")
                print("   Asegúrate de haber colocado suficientes archivos .wav en la carpeta 'calibration_data'.")
            except Exception as e:
                print(f"\n❌ ERROR INESPERADO durante la cuantización estática: {e}")
                print("   Esto puede deberse a falta de memoria RAM.")
        else:
            print(f"ℹ️ El modelo cuantizado estáticamente '{static_quant_path}' ya existe. Saltando.")
    else:
        print("\nℹ️ Saltando la cuantización estática por elección del usuario.")

    print(f"\n¡Proceso finalizado! Los modelos disponibles han sido generados en la carpeta '{ONNX_MODELS_DIR}'.")

if __name__ == "__main__":
    print("--- INICIO DEL SCRIPT DE EXPORTACIÓN DE MODELOS DE EMOCIÓN VOCAL ---")
    print("Este script descargará el modelo de Hugging Face y lo convertirá a formatos ONNX optimizados.")
    export_models()
