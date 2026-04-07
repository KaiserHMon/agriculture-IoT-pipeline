# Agriculture IoT Pipeline

Build an E2E pipeline that processes agricultural sensor data (IoT) and generates datasets ready for soil moisture, crop yield, and weather condition prediction models.

## 🏗️ Architecture
We follow the **Medallion Architecture** (Bronze, Silver, Gold). For more details, see [ARCHITECTURE.md](./docs/architecture.md).

## 🚀 Stack
- **Environment Management:** [uv](https://github.com/astral-sh/uv)
- **Languages:** Python (3.12+)
- **Cloud/Data:** AWS S3 (Data Lake), AWS Athena, AWS Lambda,  AWS Glue Data Catalog
- **Transformation:** dbt (Data Build Tool), awswrangler
- **Ops & Quality:** Ruff, Mypy, Pydantic, GitHub Actions, JSON Logging

## 🛠️ Development (with uv)

```bash
# Sync environment and install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run the ingestion script
uv run python -m ingestion.raw_to_bronze

# Run tests
$env:PYTHONPATH='.'; uv run pytest tests/
```

## 🐳 Docker Usage

To run the pipeline in a containerized environment:

```bash
# Build and run the ingestion service
docker-compose up --build

# Run tests inside the container
docker-compose run --rm ingestion uv run pytest
```

## 📂 Project Structure
```text
.
├── .github/workflows/  # CI/CD (GitHub Actions)
├── config/             # YAML configuration files
├── data/               # Local data (git-ignored)
├── ingestion/          # Bronze layer ingestion scripts
├── logs/               # JSON formatted application logs
├── transformation/     # Silver (Lambda) and Gold (dbt) logic
├── utils/              # S3 client, Config (Pydantic), Logger (JSON)
├── tests/              # Unit and integration tests
├── ARCHITECTURE.md     # Detailed design & best practices
├── README.md           # This file
└── pyproject.toml      # Dependencies and tool config
```
