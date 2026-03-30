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

## 🏗️ Architecture (Medallion Pattern)
- **Bronze (Raw):** Landing zone en S3 (`segundohardoy-data-raw-...`) para CSV y XLSX.
- **Silver (Cleaned):** Transformación mediante **AWS Lambda** a formato Parquet (Snappy). Soporta "Wide Tables" para capturar múltiples métricas (pH, humedad, etc.) dinámicamente.
- **Gold (Curated):** ML-ready agregados usando dbt sobre Athena.

## 🚀 Key Decisions
### 1. Schema-Agnostic Silver Layer
Se implementó una lógica flexible en la Lambda que limpia nombres de columnas (snake_case) y acepta cualquier métrica numérica, evitando fallos por cambios en el origen.

### 2. Data Identity Requirement
Se decidió procesar únicamente archivos con identificadores claros (`sensor_id` o `farm_id`). Archivos sin identidad estructural (ej. Excel simples de una sola métrica sin ID) fueron excluidos para mantener la integridad del Data Lake.

### 3. Resource Optimization
La Lambda fue optimizada a **512MB RAM** y **60s Timeout** para manejar la carga inicial de `awswrangler` y el procesamiento de archivos Excel pesados.


### 2. Configuration & Security
- **`.env` (Mandatory):** Stores sensitive credentials: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_S3_BUCKET` (prevents exposing Account ID).
- **`config/settings.yaml`:** Stores non-sensitive paths, prefixes, and date column names for ingestion.

### 3. File Management & Docker
The `ingestion/raw_to_bronze.py` script automatically moves successfully uploaded files from `data/input/` to `data/processed/`. The Docker setup mounts these folders to ensure data persistence between runs.

## 🧪 Current Status
- [x] S3 Client wrapper (`utils/s3_client.py`).
- [x] Configuration centralized (`config/settings.yaml`).
- [x] Ingestion script with smart partitioning (`ingestion/raw_to_bronze.py`).
- [x] Unit tests for date extraction logic (`tests/test_date_extraction.py`).
- [x] Dockerization (Dockerfile & Docker Compose).

## 🔜 Next Steps
See [NEXT_STEPS.md](./NEXT_STEPS.md) for a detailed roadmap.
