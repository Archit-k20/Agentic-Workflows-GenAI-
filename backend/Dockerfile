FROM python:3.11-slim-bookworm
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 TRACE_DATA_DIR=/data HF_HOME=/model-cache TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr nodejs default-jdk-headless gcc g++ ca-certificates ffmpeg espeak-ng libsndfile1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.lock backend/requirements-torch.lock /app/backend/
RUN pip install --no-cache-dir -r backend/requirements-torch.lock --index-url https://download.pytorch.org/whl/cpu && pip install --no-cache-dir -r backend/requirements.lock
COPY workflows /app/workflows
COPY backend /app/backend
RUN useradd --create-home --uid 10001 trace && mkdir /data /model-cache && chown trace:trace /data /model-cache
USER trace
EXPOSE 8000
CMD ["uvicorn","backend.app:app","--host","0.0.0.0","--port","8000","--no-access-log"]
