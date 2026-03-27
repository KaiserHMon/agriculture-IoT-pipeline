# Gemini Project Guide: Agriculture IoT Pipeline

This document serves as the project memory and roadmap for future Gemini CLI sessions.

## 📌 Project Overview
**Goal:** Build an E2E pipeline for agricultural sensor data (IoT) using the Medallion Architecture (S3 + Athena + dbt).

## 🛠️ Tech Stack & Environment
- **Environment:** `uv` (managed via `pyproject.toml`)
- **Containerization:** Docker & Docker Compose
- **Cloud:** AWS (S3, Athena)
- **Transformation:** dbt (Data Build Tool)

## 🏗️ Architecture (Medallion Pattern)
- **Bronze (Raw):** Landing zone in S3 for CSV and XLSX files.
- **Silver (Cleaned):** Transformation into Parquet with type-casting and schema enforcement.
- **Gold (Curated):** ML-ready aggregated datasets.

## 🚀 Key Decisions
### 1. S3 Partitioning Strategy
We use **Hive-style partitioning** based on the data's internal `timestamp` column (Gold Standard). If missing, it falls back to the file's modification date.
- Path Format: `s3://bucket/bronze/prefix/year=YYYY/month=MM/day=DD/filename.ext`

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
