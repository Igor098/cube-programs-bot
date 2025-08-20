# syntax=docker/dockerfile:1

########### builder ###########
FROM python:3.12-slim AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt

########### runtime ###########
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd -r -u 1001 appuser

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY . .
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python - <<'PY'\nimport urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/health', timeout=3)\nPY

# alembic миграции + запуск uvicorn
ENTRYPOINT ["bash", "-lc", "alembic upgrade head && exec uvicorn app.main:application --host 0.0.0.0 --port 3000 --proxy-headers --workers 2"]
