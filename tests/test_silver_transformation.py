import pandas as pd
import pytest
from transformation.bronze_to_silver import standardize_units


@pytest.fixture
def sample_sensor_df():
    """Provides a sample dataframe for transformation tests."""
    return pd.DataFrame(
        {
            "Reading ID": ["R1", "R2", "R1"],  # R1 is duplicated
            "Sensor ID": ["S1", "S1", "S1"],
            "Value": [100.0, 25.0, 100.0],
            "Unit": ["F", "C", "F"],
            "Timestamp": [
                "2024-03-30 10:00:00",
                "2024-03-30 10:05:00",
                "2024-03-30 10:00:00",
            ],
        }
    )


def test_standardize_units_conversion(sample_sensor_df):
    """Verifies that Fahrenheit is correctly converted to Celsius."""
    # Ensure column names are lowercased for the function (as per Lambda logic)
    df = sample_sensor_df.copy()
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    df_clean = standardize_units(df)

    # R1 was 100F -> (100 - 32) * 5/9 = 37.777...
    # R2 was 25C -> remains 25C
    r1_val = df_clean.loc[df_clean["reading_id"] == "R1", "value"].iloc[0]
    r1_unit = df_clean.loc[df_clean["reading_id"] == "R1", "unit"].iloc[0]

    assert pytest.approx(r1_val, 0.1) == 37.7
    assert r1_unit == "C"

    r2_val = df_clean.loc[df_clean["reading_id"] == "R2", "value"].iloc[0]
    assert r2_val == 25.0


def test_transformation_logic_pipeline(sample_sensor_df):
    """Simulates the core transformation steps of the lambda_handler including partitioning."""
    df = sample_sensor_df.copy()

    # 1. Column Normalization
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    assert "reading_id" in df.columns
    assert "sensor_id" in df.columns

    # 2. Type Casting & Partitioning
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["value"] = pd.to_numeric(df["value"])

    # Mirroring the new Lambda logic
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["day"] = df["timestamp"].dt.day

    assert all(df["year"] == 2024)
    assert all(df["month"] == 3)
    assert all(df["day"] == 30)
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])

    # 3. Deduplication (source_id + reading_id)
    df["_source_id"] = "bronze/test.csv"
    dedup_cols = ["_source_id", "reading_id"]
    df_dedup = df.drop_duplicates(subset=dedup_cols)

    assert len(df_dedup) == 2  # Originally 3, one R1 removed

    # 4. Null Management
    df_with_nulls = pd.concat(
        [
            df_dedup,
            pd.DataFrame(
                [{"reading_id": "R3", "sensor_id": None, "value": None, "unit": "C"}]
            ),
        ]
    )
    df_final = df_with_nulls.dropna(subset=["sensor_id", "value"])

    assert len(df_final) == 2
    assert df_final["sensor_id"].isnull().sum() == 0
