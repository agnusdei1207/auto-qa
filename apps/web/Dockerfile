# Web Dockerfile - Dashboard UI
FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt update && apt install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY apps/web/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY libs /app/libs
COPY apps/__init__.py /app/apps/
COPY apps/web /app/apps/web

ENV PYTHONPATH=/app
WORKDIR /app

ENV PORT=80
EXPOSE ${PORT}

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn apps.web.src.main:app --host 0.0.0.0 --port ${PORT}"]
