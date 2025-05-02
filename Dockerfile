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
CMD ["/bin/bash"]

# Development stage
FROM base AS dev
# Install additional development packages
RUN pip install pytest==8.3.5 pre-commit==4.2.0

# Default command to run your LangGraph app
CMD ["/bin/bash"]
