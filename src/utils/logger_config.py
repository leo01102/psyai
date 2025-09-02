# src/utils/logger_config.py

import logging
import os
import warnings
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configura el sistema de logging para la aplicación.
    - Un handler para la consola con nivel INFO.
    - Un handler para un archivo rotativo con nivel DEBUG.
    - Silencia los logs demasiado "ruidosos" de librerías de terceros.
    """
    # --- CONFIGURACIÓN DE WARNINGS ---
    # Ignorar warnings específicos y benignos de Keras/TensorFlow que llenan la consola.
    warnings.filterwarnings("ignore", category=UserWarning, module='keras')
    warnings.filterwarnings("ignore", message="The name tf.reset_default_graph is deprecated")

    # --- CONFIGURACIÓN DE LOGGING ---
    # Crear el directorio de logs si no existe
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 1. Crear el logger principal
    # __name__ asegura que los loggers de los módulos hereden esta configuración
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capturar todo desde el nivel DEBUG hacia arriba

    # Evitar que se dupliquen los handlers si la función se llama más de una vez
    if logger.hasHandlers():
        logger.handlers.clear()

    # 2. Crear formatter para definir el formato de los mensajes de log
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 3. Crear handler para la consola (StreamHandler)
    # Muestra solo logs de nivel INFO y superior en la terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)

    # 4. Crear handler para el archivo (RotatingFileHandler)
    # Guarda todo desde el nivel DEBUG en un archivo que rota cuando llega a 1MB.
    # Mantiene hasta 3 archivos de backup.
    log_file_path = os.path.join(log_dir, "psyai.log")
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=1024*1024, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)

    # 5. Añadir los handlers al logger principal
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # 6. Silenciar librerías "ruidosas" a un nivel superior
    # Los WARNINGS y ERRORS seguirán apareciendo.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("streamlit_webrtc").setLevel(logging.WARNING)
    logging.getLogger("aioice").setLevel(logging.WARNING)
    # Dejamos que los errores de libav/aiortc se muestren como WARNING para estar al tanto,
    # pero no llenarán el log con mensajes INFO/DEBUG.
    logging.getLogger("libav").setLevel(logging.WARNING)
    logging.getLogger("aiortc").setLevel(logging.WARNING)
