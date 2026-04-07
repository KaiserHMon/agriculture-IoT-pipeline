import os
import awswrangler as wr
import pandas as pd
from datetime import datetime
import urllib.parse
import re
from utils.logger import logger

# Configuration from validated settings/env
DATABASE = os.environ.get("GLUE_DATABASE", "agriculture_db")
TABLE = os.environ.get("GLUE_TABLE", "silver_sensor_data")
OUTPUT_PATH = os.environ.get("SILVER_S3_PATH")


def clean_column_name(name):
    """Cleans column names: lowercase, no spaces, no special characters."""
    name = str(name).lower().strip()
    name = re.sub(r"[^a-z0-9_]", "", name.replace(" ", "_"))
    return name


def standardize_units(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes metrics (e.g., Temperature F to C)."""
    if "unit" in df.columns and "value" in df.columns:
        # Convert Fahrenheit to Celsius
        mask_f = df["unit"].str.upper() == "F"
        df.loc[mask_f, "value"] = (df.loc[mask_f, "value"] - 32) * 5 / 9
        df.loc[mask_f, "unit"] = "C"
    return df


def lambda_handler(event, context):
    """
    AWS Lambda handler to transform Bronze (CSV/XLSX) to Silver (Parquet).
    """
    key = "unknown"
    try:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(
            event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
        )

        logger.info("Processing file", extra={"s3_path": f"s3://{bucket}/{key}"})

        # 1. Read data using awswrangler
        if key.lower().endswith(".csv"):
            df = wr.s3.read_csv(path=f"s3://{bucket}/{key}")
        elif key.lower().endswith(".xlsx"):
            df = wr.s3.read_excel(path=f"s3://{bucket}/{key}")
        else:
            logger.warning("Unsupported file format", extra={"file_key": key})
            return {"statusCode": 400, "body": "Unsupported format"}

        # 2. Normalize column names
        df.columns = [clean_column_name(c) for c in df.columns]

        # 2b. Standardize Units
        df = standardize_units(df)

        # 3. Validate Identity Columns
        if "sensor_id" not in df.columns:
            if "farm_id" in df.columns:
                df = df.rename(columns={"farm_id": "sensor_id"})
            else:
                raise KeyError(
                    f"Required identity columns (sensor_id or farm_id) not found. Columns: {df.columns.tolist()}"
                )

        # 4. Traceability Metadata
        df["_source_id"] = key
        df["_ingested_at"] = datetime.utcnow()

        # 5. Type Casting
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            # Create partition columns from timestamp
            df["year"] = df["timestamp"].dt.year
            df["month"] = df["timestamp"].dt.month
            df["day"] = df["timestamp"].dt.day
        else:
            # Fallback if no timestamp is present (unlikely given ingestion logic)
            now = datetime.utcnow()
            df["year"] = now.year
            df["month"] = now.month
            df["day"] = now.day

        # Convert numeric columns automatically
        non_numeric = [
            "sensor_id",
            "timestamp",
            "_source_id",
            "unit",
            "region",
            "crop_type",
            "year",
            "month",
            "day",
        ]
        for col in df.columns:
            if col not in non_numeric:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 6. Deduplication
        df = df.dropna(subset=["sensor_id"])
        dedup_cols = ["sensor_id"]
        if "timestamp" in df.columns:
            dedup_cols.append("timestamp")

        df = df.drop_duplicates(subset=dedup_cols)

        # 7. Write to Silver (S3 Parquet + Glue Catalog)
        if not OUTPUT_PATH:
            raise ValueError("SILVER_S3_PATH environment variable is not set.")

        # Partitioning like Raw: year, month, day
        # We also keep sensor_id partitioning for optimized queries if dataset grows
        partition_cols = ["year", "month", "day"]

        wr.s3.to_parquet(
            df=df,
            path=OUTPUT_PATH,
            dataset=True,
            database=DATABASE,
            table=TABLE,
            mode="append",
            partition_cols=partition_cols,
            compression="snappy",
        )

        logger.info(
            "Successfully processed file", extra={"rows": len(df), "table": TABLE}
        )
        return {"statusCode": 200, "body": "Success"}

    except Exception as e:
        logger.error(
            "Critical error in transformation", extra={"file_key": key, "error": str(e)}
        )
        raise e
