# Architecture & Design Decisions

This document outlines the technical architecture and engineering standards for the Agriculture IoT Pipeline.

## 1. Data Lake Architecture: Medallion Pattern
We follow the **Medallion Architecture** to ensure data quality and traceability as it moves through the pipeline.

| Tier | Format | Description |
| :--- | :--- | :--- |
| **Bronze (Raw)** | CSV/XLSX | Immutable landing zone for source data. No transformations. |
| **Silver (Cleaned)** | Parquet | Type casting, deduplication, and schema enforcement using **AWS Lambda**. |
| **Gold (Curated)** | Parquet | Aggregated, ML-ready datasets (e.g., Daily Soil Moisture Averages) using **Athena/dbt**. |

## 2. Technology Stack
- **Ingestion:** Python (boto3) for uploading local files to S3.
- **Storage:** AWS S3 (Data Lake) with separate buckets for Raw and Silver tiers.
- **Transformation (B->S):** AWS Lambda for serverless, event-driven processing (CSV to Parquet).
  - **Logic:** Dynamic Schema (Wide Table), snake_case normalization, removal of special characters (e.g., '%', ' (C)'), and identity fallback (`farm_id` as `sensor_id` if missing).
  - **Deduplication:** Uses `sensor_id` + `timestamp` + `reading_id` to ensure idempotency.
- **Transformation (S->G):** AWS Athena for serverless SQL and dbt (Data Build Tool) for logic management.

## 3. Best Practices
### Partitioning
To optimize query cost and performance in Athena, data is stored using Hive-style partitioning:
`s3://my-bucket/bronze/sensor_data/year=YYYY/month=MM/day=DD/`
The Lambda function maintains this partitioning in the Silver layer.

### Idempotency
Pipeline runs are designed to be repeatable. Running an ingestion script twice should result in the same final state without duplicates.

### Environment Management
- All secrets (AWS Keys) are stored in a `.env` file (never committed).
- Local data for development is kept in `data/input` and `data/output` (ignored by Git).

### Schema Evolution
Transformations must handle changes in sensor firmware (e.g., added/removed columns) without breaking the entire downstream pipeline.
