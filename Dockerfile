# Use official lightweight Python runtime
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/backend:/app"

WORKDIR /app

# Install dependencies first for layer caching
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend codebase, datasets, and configuration
COPY backend/ ./backend/
COPY data/ ./data/

# Expose API port (8000) and Gradio fallback port (7860)
EXPOSE 8000 7860

# Default: Launch operations-grade FastAPI service
WORKDIR /app/backend
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
