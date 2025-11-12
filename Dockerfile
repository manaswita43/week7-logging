# Dockerfile (put at repo root)
FROM python:3.11-slim

# Create app directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and model folder
COPY app/ /app/

# Environment - default model path (can be overridden by k8s env)
ENV MODEL_PATH=/app/models/model.joblib

# Expose port used by uvicorn
EXPOSE 8200

# Run with multiple workers for per-pod concurrency
# Using uvicorn --workers to allow per-pod concurrency
CMD ["uvicorn", "log:app", "--host", "0.0.0.0", "--port", "8200", "--workers", "4"]