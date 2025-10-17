# Simple production Dockerfile for Russekort Digital
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# System deps (optional: add libffi, etc., but Pillow works on slim)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy app and install requirements
COPY Russekort/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY Russekort ./Russekort

# Create storage dirs at image build time (also ensured at runtime)
RUN mkdir -p /app/Russekort/backend/storage/cards /app/Russekort/backend/storage/qrcodes

# Create non-root user and set ownership
RUN useradd -m -u 10001 appuser \
  && chown -R appuser:appuser /app

USER appuser

# Expose port and run server
EXPOSE 8080
CMD ["sh", "-c", "python -m uvicorn Russekort.backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
