# --- build stage ---
FROM python:3.11-slim AS builder
WORKDIR /app

# системные пакеты (psycopg2 требует libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# --- runtime stage ---
FROM python:3.11-slim
WORKDIR /app

# системные зависимости для psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# создадим непривилегированного пользователя
RUN useradd -m appuser
USER appuser

# скопируем колёса и установим
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# скопируем проект (минимально нужное)
COPY . .

# по умолчанию Uvicorn, но команду зададим в compose
ENV PYTHONUNBUFFERED=1

HEALTHCHECK CMD curl -f http://localhost:8000/healthz || exit 1
