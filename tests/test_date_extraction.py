import os
import pandas as pd
import pytest
from datetime import datetime
from ingestion.raw_to_bronze import get_data_date


@pytest.fixture
def temp_data_dir(tmp_path):
    """Creates a temporary directory for test files."""
    d = tmp_path / "data"
    d.mkdir()
    return d


def test_extract_date_from_csv(temp_data_dir):
    # Create a dummy CSV with a 'timestamp' column
    file_path = temp_data_dir / "test_sensors.csv"
    df = pd.DataFrame(
        {"timestamp": ["2024-05-20 10:00:00"], "sensor_id": ["S1"], "value": [25.5]}
    )
    df.to_csv(file_path, index=False)

    extracted_date = get_data_date(str(file_path), ["timestamp"])
    assert extracted_date.year == 2024
    assert extracted_date.month == 5
    assert extracted_date.day == 20


def test_extract_date_from_csv_different_column(temp_data_dir):
    # Create a dummy CSV with a 'sowing_date' column
    file_path = temp_data_dir / "test_crops.csv"
    df = pd.DataFrame({"sowing_date": ["2023-11-15"], "crop": ["Wheat"]})
    df.to_csv(file_path, index=False)

    extracted_date = get_data_date(str(file_path), ["timestamp", "sowing_date"])
    assert extracted_date.year == 2023
    assert extracted_date.month == 11
    assert extracted_date.day == 15


def test_fallback_to_file_date(temp_data_dir):
    # Create a dummy CSV without any date columns
    file_path = temp_data_dir / "no_date.csv"
    df = pd.DataFrame({"id": [1], "data": ["test"]})
    df.to_csv(file_path, index=False)

    # Get file modification time
    mod_time = datetime.fromtimestamp(os.path.getmtime(str(file_path)))

    extracted_date = get_data_date(str(file_path), ["timestamp"])

    # It should fallback to file date (allowing for slight precision differences)
    assert extracted_date.year == mod_time.year
    assert extracted_date.month == mod_time.month
    assert extracted_date.day == mod_time.day


def test_extract_date_from_excel(temp_data_dir):
    # Create a dummy Excel with 'timestamp'
    file_path = temp_data_dir / "test.xlsx"
    df = pd.DataFrame({"timestamp": [datetime(2022, 1, 1)], "value": [10]})
    df.to_excel(file_path, index=False)

    extracted_date = get_data_date(str(file_path), ["timestamp"])
    assert extracted_date.year == 2022
    assert extracted_date.month == 1
    assert extracted_date.day == 1
