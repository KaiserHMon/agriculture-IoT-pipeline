import os
from dotenv import load_dotenv
from ingestion.raw_to_bronze import run_ingestion
from utils.logger import logger

# 1. Cargar variables de entorno del archivo .env
load_dotenv()

def main():
    """
    Punto de entrada principal para el pipeline de IoT Agrícola.
    """
    logger.info("=== Iniciando Ejecución del Pipeline E2E ===")
    
    try:
        # Ejecutar Fase 1: Ingestión (Local -> S3 Bronze)
        run_ingestion()
        
        logger.info("=== Ejecución completada exitosamente ===")
        logger.info("Verifica los resultados en tu bucket de S3 Bronze.")
        
    except Exception as e:
        logger.error(f"Error crítico durante la ejecución: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
