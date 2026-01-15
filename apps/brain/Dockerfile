# Brain Dockerfile - Multi-Agent QA System
FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt update && apt install -y --no-install-recommends \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN cat /tmp/requirements.txt && pip install --no-cache-dir -r /tmp/requirements.txt

COPY libs /app/libs
COPY apps/__init__.py /app/apps/
COPY apps/brain /app/apps/brain

ENV PYTHONPATH=/app
WORKDIR /app

ENV PORT=9000
EXPOSE ${PORT}

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn apps.brain.src.main:app --host 0.0.0.0 --port ${PORT}"]
