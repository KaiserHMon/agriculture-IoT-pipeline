import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name="agriculture_iot", log_dir="logs"):
    """
    Configura un logger que escribe tanto en consola como en un archivo rotativo.
    """
    # Crear directorio de logs si no existe
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Evitar duplicados si el logger ya está configurado
    if logger.handlers:
        return logger

    # Formato del log
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler para Consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para Archivo (Rotativo: 5MB por archivo, máximo 5 archivos)
    log_filename = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = RotatingFileHandler(
        log_filename, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Instancia global para fácil acceso
logger = setup_logger()
