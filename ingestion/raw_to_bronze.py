import os
import shutil
import pandas as pd
from datetime import datetime
from utils.s3_client import S3Client
from utils.logger import logger
from utils.config import settings


def get_data_date(file_path, date_columns):
    """
    Attempts to extract the date from the data's timestamp column.
    Falls back to file modification time if column is missing or file is not readable.
    """
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, nrows=1)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, nrows=1)
        else:
            return datetime.fromtimestamp(os.path.getmtime(file_path))

        for col in date_columns:
            if col in df.columns:
                return pd.to_datetime(df[col].iloc[0])

    except Exception as e:
        logger.warning(
            f"Could not extract date from data in {file_path}: {e}. Using file date."
        )

    return datetime.fromtimestamp(os.path.getmtime(file_path))


def run_ingestion():
    """
    Scans input_dir for files, uploads them to S3 Bronze layer, and moves them to processed_dir.
    """
    # 1. Initialize S3 Client
    bucket_name = settings.s3.bucket_name
    if not bucket_name:
        logger.error("AWS_S3_BUCKET is not set in environment variables.")
        return

    s3 = S3Client(bucket_name=bucket_name)

    input_dir = settings.paths.input_dir
    processed_dir = settings.paths.processed_dir
    bronze_prefix = settings.s3.bronze_prefix

    # Ensure directories exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    # 2. Scan for files
    allowed_ext = tuple(settings.ingestion.allowed_extensions)
    files_to_upload = [f for f in os.listdir(input_dir) if f.endswith(allowed_ext)]

    if not files_to_upload:
        logger.info(f"No new files found in {input_dir} to upload.")
        return

    logger.info(f"Found {len(files_to_upload)} files to upload.")

    # 3. Upload and Move each file
    for filename in files_to_upload:
        local_path = os.path.join(input_dir, filename)

        # Determine the date for partitioning
        record_date = get_data_date(local_path, settings.ingestion.date_columns)
        partition_path = s3.generate_partition_path(bronze_prefix, record_date)

        s3_key = f"{partition_path}{filename}"

        success = s3.upload_file(local_path, s3_key)

        if success:
            logger.info(f"Successfully uploaded {filename} to {s3_key}")

            # Move file to processed directory
            dest_path = os.path.join(processed_dir, filename)

            # Handle potential filename collisions in processed folder
            if os.path.exists(dest_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(processed_dir, f"{name}_{timestamp}{ext}")

            shutil.move(local_path, dest_path)
            logger.info(f"Moved {filename} to {processed_dir}")
        else:
            logger.error(f"Failed to upload {filename}. Skipping move.")


if __name__ == "__main__":
    run_ingestion()
