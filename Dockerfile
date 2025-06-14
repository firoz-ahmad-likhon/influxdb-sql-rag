FROM python:3.11-slim AS base

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Production stage
FROM base AS prod
# Default command to run your LangGraph app
CMD ["uvicorn", "api.rag:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "."]

# Development stage
FROM base AS dev
# Install additional development packages
RUN pip install pytest==8.3.5

# Default command to run your LangGraph app
CMD ["uvicorn", "api.rag:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "."]
