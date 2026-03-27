# Agriculture IoT Pipeline

Build an E2E pipeline that processes agricultural sensor data (IoT) and generates datasets ready for soil moisture, crop yield, and weather condition prediction models.

## 🏗️ Architecture
We follow the **Medallion Architecture** (Bronze, Silver, Gold). For more details, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## 🚀 Stack
- **Environment Management:** [uv](https://github.com/astral-sh/uv)
- **Languages:** Python
- **Cloud/Data:** AWS S3 (Data Lake), AWS Athena
- **Transformation:** dbt (Data Build Tool)
- **Libs:** boto3, pandas, openpyxl, pyyaml, pytest

## 🛠️ Development (with uv)

```bash
# Sync environment and install dependencies
uv sync

# Run the ingestion script
uv run python -m ingestion.raw_to_bronze

# Run tests
uv run pytest
```

## 🐳 Docker Usage

To run the pipeline in a containerized environment:

```bash
# Build and run the ingestion service
docker-compose up --build

# Run tests inside the container
docker-compose run --rm ingestion uv run pytest
```

Ensure your `.env` file is configured correctly as it will be loaded by the container.

## 📂 Project Structure
```text
.
├── config/             # Configuration for AWS and dbt
├── data/               # Local data (git-ignored)
│   ├── input/          # .csv / .xlsx source files
│   └── processed/      # Successfully uploaded files
├── ingestion/          # Scripts for S3 uploads (boto3)
├── logs/               # Application logs
├── transformation/     # dbt models and SQL logic
├── utils/              # S3 client and common helpers
├── tests/              # Data validation and unit tests
├── ARCHITECTURE.md     # Detailed design & best practices
├── README.md           # This file
└── pyproject.toml      # Dependencies
```
