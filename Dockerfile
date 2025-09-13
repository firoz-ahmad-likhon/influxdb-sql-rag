FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY src/ src/
COPY api/ api/

# Production stage
FROM base AS prod
# Default command to run your LangGraph app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "."]

# Development stage
FROM base AS dev
# Install dev-specific Python tools
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Default command to run your LangGraph app
CMD ["uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "."]
