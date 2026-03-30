# Roadmap: Completing the E2E Agriculture IoT Pipeline

This document outlines the remaining phases to transform your "Bronze" data into "Gold" datasets ready for ML.

---

## Phase 2: Bronze to Silver (AWS Lambda) - [COMPLETED]
- [x] **Lambda Function Development:** `transformation/bronze_to_silver.py` implemented (Wide Table approach).
- [x] **Core Logic:** Flexible schema, deduplication, and identity mapping.
- [x] **Infrastructure Setup:** IAM Policies, Memory (512MB), and Timeout (60s) optimized.
- [x] **Deployment Verification:** Confirmed E2E flow from local upload to Silver Parquet.

## Phase 3: Silver to Gold (Athena + dbt) - [NEXT UP]
Once data is in Silver (Parquet), we use dbt to create business-ready datasets.

- [ ] **dbt Setup:**
  - [ ] Install `dbt-athena-community`.
  - [ ] Initialize dbt project: `dbt init agriculture_dbt`.
  - [ ] Configure `profiles.yml` for AWS Athena connection.
- [ ] **Silver Models:**
  - [ ] Define staging models to standardize the `silver_sensor_data` table.
- [ ] **Gold Layer (Curated Models):**
  - [ ] Create dbt models for aggregations (e.g., `daily_sensor_averages`).
  - Join sensor data with farm/crop metadata.
  - Materialize these as tables in S3 (Parquet format).

---

## Phase 4: Data Quality & Monitoring
Ensure the pipeline is reliable and the data is trustworthy.

- [ ] **dbt Tests:** Add `not_null`, `unique`, and `accepted_values` tests to Gold models.
- [ ] **CloudWatch Logs:** Monitor Lambda execution and set up alerts for transformation failures.
- [ ] **Data Validation:** Implement checks to ensure no data loss during the B->S conversion.

---

## Phase 5: Consumption & ML Readiness
The final step is making the data available for your prediction models.

- [ ] **Gold Export:** Ensure the Gold layer is easily queryable via Athena.
- [ ] **Feature Engineering:** Document the final features available for Soil Moisture/Yield models.
- [ ] **CI/CD:** Automate dbt runs using a scheduler or GitHub Actions.

---

### How to use this roadmap:
La Phase 2 ya tiene el código listo. El siguiente gran hito es la Phase 3 para empezar a usar dbt sobre los datos que la Lambda ya está limpiando.
