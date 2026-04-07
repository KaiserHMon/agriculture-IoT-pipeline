import os
import yaml
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class S3Config(BaseModel):
    bronze_prefix: str = Field(..., description="S3 prefix for the Bronze layer")
    bucket_name: str = Field(default_factory=lambda: os.getenv("AWS_S3_BUCKET", ""))


class PathConfig(BaseModel):
    input_dir: str
    processed_dir: str


class IngestionConfig(BaseModel):
    allowed_extensions: List[str]
    date_columns: List[str]


class Settings(BaseModel):
    s3: S3Config
    paths: PathConfig
    ingestion: IngestionConfig

    @classmethod
    def load_from_yaml(cls, path: str = "config/settings.yaml") -> "Settings":
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        return cls(**data)


# Global settings instance
try:
    settings = Settings.load_from_yaml()
except Exception as e:
    # We fallback to a dummy if loading fails during a dry-run or CI
    # but in production, we want this to fail loudly.
    import logging

    logging.error(f"Failed to load settings: {e}")
    raise e
