FROM python:3.11-slim AS base

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY pages/ pages/

# Production stage
FROM base AS prod

EXPOSE 8501

CMD ["streamlit", "run", "pages/app.py", "--server.address=0.0.0.0"]

# Development stage
FROM base AS dev

EXPOSE 8501

CMD ["streamlit", "run", "pages/app.py", "--server.address=0.0.0.0", "--server.runOnSave=true"]
