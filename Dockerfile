# ===========================
# Base Image
# ===========================
FROM python:3.12-slim

# ===========================
# Environment Variables
# ===========================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ===========================
# Working Directory
# ===========================
WORKDIR /app

# ===========================
# System Dependencies
# Remove gcc/libpq-dev if you're using psycopg2-binary
# ===========================
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl && \
    rm -rf /var/lib/apt/lists/*

# ===========================
# Install Python Dependencies
# ===========================
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ===========================
# Copy Application
# ===========================
COPY . .

# ===========================
# Create Non-root User
# ===========================
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

# ===========================
# Expose Port
# ===========================
EXPOSE 8000

# ===========================
# Health Check
# ===========================
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
CMD curl --fail http://localhost:8000/health || exit 1

# ===========================
# Start Server
# ===========================
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--workers", "3", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
