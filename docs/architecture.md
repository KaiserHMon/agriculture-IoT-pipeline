# Architecture & Design Decisions

This document outlines the technical architecture and engineering standards for the Agriculture IoT Pipeline.

## 1. Data Lake Architecture: Medallion Pattern
We follow the **Medallion Architecture** to ensure data quality and traceability as it moves through the pipeline.

| Tier | Format | Description |
| :--- | :--- | :--- |
| **Bronze (Raw)** | CSV/XLSX | Immutable landing zone. Particionado por `year/month/day` de carga o de dato. |
| **Silver (Cleaned)** | Parquet | Limpieza, tipado y particionamiento por `year/month/day` del dato vía **AWS Lambda**. |
| **Gold (Curated)** | Parquet | Agregados y datasets listos para ML usando **Athena + dbt**. |

## 2. Technology Stack
- **Ingestion:** Python (boto3) con validación de configuración vía **Pydantic**.
- **Storage:** AWS S3 con particionamiento Hive-style.
- **Transformation (B->S):** AWS Lambda (awswrangler).
  - **Schema-Agnostic:** Limpieza de nombres a `snake_case` y conversión automática de métricas.
  - **Partitioning:** Los datos en Silver se guardan particionados por `year`, `month` y `day` extraídos del `timestamp` original.
  - **Standardization:** Conversión automática de unidades (ej. Fahrenheit a Celsius).
- **Observability:** Logs estructurados en formato **JSON** para integración nativa con CloudWatch.

## 3. Engineering Standards & Best Practices

### CI/CD & Quality
- **Linting & Formatting:** Se utiliza **Ruff** para mantener la consistencia del código.
- **Type Checking:** Uso estricto de **Mypy** con stubs para pandas y pydantic.
- **Automated Testing:** Pipeline de GitHub Actions que valida cada cambio antes del merge a `main`.

### Partitioning & Performance
Para optimizar costos y velocidad en Athena, todas las capas utilizan particionamiento Hive-style:
`s3://bucket/tier/table/year=YYYY/month=MM/day=DD/`
Esto permite que Athena realice "Partition Pruning", leyendo solo los datos necesarios.

### Configuration Management
La configuración no es un simple diccionario; es un objeto validado por **Pydantic**. Esto garantiza que si falta una variable de entorno o un path en el YAML, el error se detecta en milisegundos al iniciar la aplicación.

### Environment Management
- Secrets via `.env`.
- Dependencias gestionadas por `uv` para instalaciones ultra-rápidas y reproducibles.
