import boto3
import os
import logging
from typing import Optional
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class S3Client:
    """
    A simple wrapper for S3 operations using boto3.
    """

    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or os.getenv("AWS_S3_BUCKET")

        self.region = os.getenv("AWS_REGION", "us-east-1")

        # Initialize the S3 client
        self.client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
        )

    def generate_partition_path(self, base_prefix: str, date_obj) -> str:
        """
        Generates a Hive-style partition path: prefix/year=YYYY/month=MM/day=DD/

        :param base_prefix: The starting folder (e.g., 'raw/sensor_data')
        :param date_obj: A datetime object to extract YYYY, MM, DD
        :return: String path
        """
        year = date_obj.strftime("%Y")
        month = date_obj.strftime("%m")
        day = date_obj.strftime("%d")
        return f"{base_prefix.strip('/')}/year={year}/month={month}/day={day}/"

    def upload_file(self, local_path: str, s3_key: str) -> bool:
        """
        Uploads a file to the S3 bucket.

        :param local_path: Path to the local file.
        :param s3_key: S3 object key (e.g., 'bronze/sensor_data/file.csv').
        :return: True if upload was successful, False otherwise.
        """
        try:
            logger.info(
                f"Uploading {local_path} to s3://{self.bucket_name}/{s3_key}..."
            )
            self.client.upload_file(local_path, self.bucket_name, s3_key)
            logger.info("Upload successful.")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False
        except FileNotFoundError:
            logger.error(f"The file {local_path} was not found.")
            return False

    def list_objects(self, prefix: str = "") -> list:
        """
        Lists objects in the bucket with a given prefix.
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except ClientError as e:
            logger.error(f"Error listing objects: {e}")
            return []

    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Downloads a file from S3 to a local path.
        """
        try:
            logger.info(
                f"Downloading s3://{self.bucket_name}/{s3_key} to {local_path}..."
            )
            self.client.download_file(self.bucket_name, s3_key, local_path)
            return True
        except ClientError as e:
            logger.error(f"Failed to download {s3_key}: {e}")
            return False
