# Gemini Project Guide: Agriculture IoT Pipeline

This document serves as the project memory and roadmap for future Gemini CLI sessions.

## 📌 Project Overview
**Goal:** Build an E2E pipeline for agricultural sensor data (IoT) using the Medallion Architecture (S3 + Athena + dbt).

## 🛠️ Tech Stack & Environment
- **Environment:** `uv` (managed via `pyproject.toml`)
- **Containerization:** Docker & Docker Compose
- **Cloud:** AWS (S3, Lambda, Glue, Athena)
- **Transformation (B->S):** AWS Lambda (Python + awswrangler) - *Schema-Agnostic Wide Table Approach*.
- **Transformation (S->G):** dbt (Data Build Tool) + Athena.
- **Quality & Ops:** Ruff (Linting), Mypy (Types), GitHub Actions (CI), Pydantic (Config Validation), JSON Logging.

## 🏗️ Architecture (Medallion Pattern)
- **Bronze (Raw):** Landing zone en S3 para CSV y XLSX. Particionado por fecha (`year/month/day`).
- **Silver (Cleaned):** Transformación mediante **AWS Lambda** a formato Parquet (Snappy). Mantiene el particionamiento por fecha y soporta "Wide Tables".
- **Gold (Curated):** ML-ready agregados usando dbt sobre Athena.

## 🚀 Key Decisions
### 1. Schema-Agnostic Silver Layer
Se implementó una lógica flexible en la Lambda que limpia nombres de columnas (snake_case) y acepta cualquier métrica numérica, evitando fallos por cambios en el origen.

### 2. Data Identity Requirement
Se decidió procesar únicamente archivos con identificadores claros (`sensor_id` o `farm_id`).

### 3. Incremental & Partitioned Processing
Tanto la capa Bronze como la Silver están particionadas por `year`, `month` y `day` extraídos del `timestamp` del dato, optimizando costos de Athena y permitiendo procesamiento incremental.

### 4. Configuration & Security
- **Pydantic Validation:** La configuración (`settings.yaml`) se valida mediante modelos de Pydantic al inicio de la ejecución.
- **Structured Logging:** Se utiliza `python-json-logger` para emitir logs en formato JSON, facilitando la observabilidad en CloudWatch.
- **CI/CD:** Pipeline en GitHub Actions que ejecuta tests, Ruff y Mypy en cada Pull Request.

## 🧪 Current Status
- [x] S3 Client wrapper (`utils/s3_client.py`).
- [x] Configuration with Pydantic validation (`utils/config.py`).
- [x] Structured JSON Logging (`utils/logger.py`).
- [x] Ingestion script with smart partitioning (`ingestion/raw_to_bronze.py`).
- [x] Silver Transformation with date partitioning (`transformation/bronze_to_silver.py`).
- [x] CI/CD Pipeline (GitHub Actions + pre-commit).
- [x] Unit tests for ingestion and transformation logic.

## 🔜 Next Steps
See [NEXT_STEPS.md](./NEXT_STEPS.md) for a detailed roadmap.
