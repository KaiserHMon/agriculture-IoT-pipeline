# Architecture & Design Decisions

This document outlines the technical architecture and engineering standards for the Agriculture IoT Pipeline.

## 1. Data Lake Architecture: Medallion Pattern
We follow the **Medallion Architecture** to ensure data quality and traceability as it moves through the pipeline.

| Tier | Format | Description |
| :--- | :--- | :--- |
| **Bronze (Raw)** | CSV/XLSX | Immutable landing zone for source data. No transformations. |
| **Silver (Cleaned)** | Parquet | Type casting, deduplication, and schema enforcement using **Athena/dbt**. |
| **Gold (Curated)** | Parquet | Aggregated, ML-ready datasets (e.g., Daily Soil Moisture Averages). |

## 2. Technology Stack
- **Ingestion:** Python (boto3) for uploading local files to S3.
- **Storage:** AWS S3 (Data Lake).
- **Compute/Query:** AWS Athena for serverless SQL queries.
- **Transformation:** dbt (Data Build Tool) for managing SQL logic and dependencies.

## 3. Best Practices
### Partitioning
To optimize query cost and performance in Athena, data is stored using Hive-style partitioning:
`s3://my-bucket/bronze/sensor_data/year=YYYY/month=MM/day=DD/`

### Idempotency
Pipeline runs are designed to be repeatable. Running an ingestion script twice should result in the same final state without duplicates.

### Environment Management
- All secrets (AWS Keys) are stored in a `.env` file (never committed).
- Local data for development is kept in `data/input` and `data/output` (ignored by Git).

### Schema Evolution
Transformations must handle changes in sensor firmware (e.g., added/removed columns) without breaking the entire downstream pipeline.
