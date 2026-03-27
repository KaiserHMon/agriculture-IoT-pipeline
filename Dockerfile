# Use a lightweight Python base image
FROM ghcr.io/astral-sh/uv:python3.12-alpine

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project configuration files
COPY pyproject.toml uv.lock* ./

# Install the project dependencies (using uv for efficiency)
RUN uv sync --frozen --no-dev

# Copy the rest of the application code
COPY config/ ./config/
COPY ingestion/ ./ingestion/
COPY utils/ ./utils/

# Ensure the required directories exist inside the container
RUN mkdir -p data/input data/processed logs

# Command to run the ingestion script by default
CMD ["uv", "run", "python", "-m", "ingestion.raw_to_bronze"]
