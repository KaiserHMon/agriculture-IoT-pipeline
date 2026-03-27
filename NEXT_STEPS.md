# Roadmap: Completing the E2E Agriculture IoT Pipeline

This document outlines the four remaining phases to transform your "Bronze" data into "Gold" datasets ready for ML.

---

## Phase 2: Infrastructure & Athena (The Entry Point)
Before we can use SQL for transformations, we must tell AWS Athena where our S3 data is.

- [ ] **S3 Cleanup:** Ensure your bucket follows the `bronze/agriculture_sensors/` structure.
- [ ] **Glue Crawler (Optional but recommended):** Create a crawler to automatically detect schemas.
- [ ] **Athena DDL:** Create the `bronze_sensor_data` external table.
  ```sql
  -- Example DDL
  CREATE EXTERNAL TABLE IF NOT EXISTS agriculture_db.bronze_sensor_data (
    reading_id string,
    sensor_id string,
    value double,
    timestamp timestamp
  )
  PARTITIONED BY (year string, month string, day string)
  STORED AS TEXTFILE
  LOCATION 's3://your-bucket/bronze/agriculture_sensors/';
  ```
- [ ] **MSCK REPAIR TABLE:** Run this in Athena to discover the partitions we created with our Python script.

---

## Phase 3: Transformation with dbt (The Brain)
This is where we turn CSVs into optimized Parquet files.

- [ ] **dbt Setup:**
  - Install `dbt-athena-community`.
  - Create a `profiles.yml` to connect to your AWS account.
- [ ] **Silver Layer (Staging):**
  - Create dbt models to cast strings to correct types.
  - Handle null values and deduplicate data.
  - **Storage:** Configure dbt to save these as `PARQUET` for performance.
- [ ] **Gold Layer (Curated):**
  - Create models for "Daily Average Soil Moisture" or "Crop Yield per Farm".
  - Join sensor data with farm metadata.

---

## Phase 4: Data Quality & Monitoring (The Guardrails)
Ensure the pipeline is reliable and the data is trustworthy.

- [ ] **dbt Tests:** Add `not_null`, `unique`, and `accepted_values` tests to your dbt YAML files.
- [ ] **Logging:** Implement a `utils/logger.py` to capture errors during ingestion and store them in the `logs/` folder.
- [ ] **Alerts:** (Optional) Set up an SNS topic to notify you if an ingestion fail or a dbt test fails.

---

## Phase 5: Consumption & ML Readiness
The final step is making the data available for your prediction models.

- [ ] **Gold Export:** Ensure the Gold layer is easily queryable via Athena or can be downloaded as a clean Parquet/CSV.
- [ ] **Feature Engineering Documentation:** Document the final features (columns) available for your Soil Moisture/Yield models.
- [ ] **CI/CD:** Automate the running of tests and ingestion using GitHub Actions or a simple local orchestrator.

---

### How to use this roadmap:
Take one step at a time! I recommend starting with **Phase 2 (Athena DDL)** in our next session to verify you can query your uploaded files.
