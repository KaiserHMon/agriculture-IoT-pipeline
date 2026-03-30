import os
import boto3
import awswrangler as wr
import pandas as pd
from datetime import datetime
import urllib.parse
import logging
import re

# Configuración de Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Variables de Entorno
DATABASE = os.environ.get("GLUE_DATABASE", "agriculture_db")
TABLE = os.environ.get("GLUE_TABLE", "silver_sensor_data")
OUTPUT_PATH = os.environ.get("SILVER_S3_PATH")

def clean_column_name(name):
    """Limpia nombres de columnas: minúsculas, sin espacios, sin caracteres especiales."""
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9_]', '', name.replace(' ', '_'))
    return name

def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        
        logger.info(f"Procesando archivo: s3://{bucket}/{key}")

        # 1. Leer datos
        if key.endswith('.csv'):
            df = wr.s3.read_csv(path=f"s3://{bucket}/{key}")
        elif key.endswith('.xlsx'):
            df = wr.s3.read_excel(path=f"s3://{bucket}/{key}")
        else:
            return

        # 2. Normalizar nombres de columnas (limpieza profunda)
        df.columns = [clean_column_name(c) for c in df.columns]
        logger.info(f"Columnas limpias: {df.columns.tolist()}")

        # 3. Validar columnas mínimas de identidad
        if 'sensor_id' not in df.columns:
            # Si no hay sensor_id, intentamos usar farm_id como identidad
            if 'farm_id' in df.columns:
                df = df.rename(columns={'farm_id': 'sensor_id'})
            else:
                raise KeyError(f"No se encontró sensor_id ni farm_id. Columnas: {df.columns.tolist()}")

        # 4. Metadatos de Trazabilidad
        df['_source_id'] = key
        df['_ingested_at'] = datetime.utcnow()
        
        # 5. Type Casting Automático
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Intentar convertir todas las columnas numéricas
        for col in df.columns:
            if col not in ['sensor_id', 'timestamp', '_source_id', 'unit', 'region', 'crop_type']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 6. Deduplicación e Idempotencia
        df = df.dropna(subset=['sensor_id'])
        
        dedup_cols = ['sensor_id']
        if 'timestamp' in df.columns: dedup_cols.append('timestamp')
        if 'reading_id' in df.columns: dedup_cols.append('reading_id')
        
        df = df.drop_duplicates(subset=dedup_cols)

        # 7. Guardar en Silver (S3 + Glue Catalog)
        if not OUTPUT_PATH: raise ValueError("Falta SILVER_S3_PATH")

        # awswrangler se encarga de añadir nuevas columnas al Glue Catalog si el CSV cambia
        wr.s3.to_parquet(
            df=df,
            path=OUTPUT_PATH,
            dataset=True,
            database=DATABASE,
            table=TABLE,
            mode="append",
            partition_cols=["sensor_id"] if len(df) > 100 else None, # Particionamos por sensor si hay muchos datos
            compression="snappy"
        )

        logger.info(f"Éxito total: {len(df)} filas procesadas de {key}")
        return {'statusCode': 200, 'body': 'Procesado exitosamente.'}

    except Exception as e:
        logger.error(f"Error crítico en {key}: {str(e)}")
        raise e
