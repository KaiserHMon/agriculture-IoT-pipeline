import os
import pytest
from unittest.mock import patch
from ingestion.raw_to_bronze import run_ingestion


@pytest.fixture
def mock_dirs(tmp_path):
    """Creates mock input and processed directories."""
    input_dir = tmp_path / "input"
    processed_dir = tmp_path / "processed"
    input_dir.mkdir()
    processed_dir.mkdir()
    return input_dir, processed_dir


@patch("ingestion.raw_to_bronze.S3Client")
@patch("ingestion.raw_to_bronze.settings")
def test_ingestion_upload_and_move(mock_settings, mock_s3_client_class, mock_dirs):
    """Verifies that ingestion scans files, 'uploads' them, and moves them to processed folder."""
    input_dir, processed_dir = mock_dirs

    # 1. Setup Mocks
    mock_settings.s3.bucket_name = "test-bucket"
    mock_settings.s3.bronze_prefix = "bronze/test/"
    mock_settings.paths.input_dir = str(input_dir)
    mock_settings.paths.processed_dir = str(processed_dir)
    mock_settings.ingestion.allowed_extensions = [".csv"]
    mock_settings.ingestion.date_columns = ["timestamp"]

    # Create a dummy file in input_dir
    test_file = input_dir / "data_2024.csv"
    test_file.write_text("timestamp,value\n2024-03-30 12:00:00,10.5")

    # Mock S3 Client behavior
    mock_s3_instance = mock_s3_client_class.return_value
    mock_s3_instance.upload_file.return_value = True
    mock_s3_instance.generate_partition_path.return_value = (
        "bronze/test/year=2024/month=03/day=30/"
    )

    # 2. Run Ingestion
    run_ingestion()

    # 3. Assertions
    # Verify S3 upload was called
    assert mock_s3_instance.upload_file.called

    # Verify file was moved from input to processed
    assert not os.path.exists(str(test_file))
    processed_file = processed_dir / "data_2024.csv"
    assert os.path.exists(str(processed_file))


@patch("ingestion.raw_to_bronze.settings")
def test_ingestion_no_files(mock_settings, mock_dirs):
    """Ensures ingestion handles empty input directory gracefully."""
    input_dir, processed_dir = mock_dirs
    mock_settings.paths.input_dir = str(input_dir)
    mock_settings.paths.processed_dir = str(processed_dir)
    mock_settings.ingestion.allowed_extensions = [".csv"]

    # No files in input_dir
    with patch("ingestion.raw_to_bronze.S3Client") as mock_s3:
        run_ingestion()
        assert not mock_s3.return_value.upload_file.called
