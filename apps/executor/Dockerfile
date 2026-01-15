# Executor Dockerfile - Playwright Web Automation
FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt update && apt install -y --no-install-recommends \
    wget \
    gnupg \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libpango-1.0-0 \
    libcairo2 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libatk-bridge2.0-0 \
    libepoxy0 \
    libdrm2 \
    libgbm1 \
    libgl1 \
    libegl1 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libxtst6 \
    libpulse0 \
    libx11-6 \
    libxrender1 \
    libxrandr2 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY libs /app/libs
COPY apps/__init__.py /app/apps/
COPY apps/executor /app/apps/executor

RUN playwright install --with-deps chromium

ENV PYTHONPATH=/app
WORKDIR /app

ENV PORT=9001
EXPOSE ${PORT}

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "uvicorn apps.executor.src.main:app --host 0.0.0.0 --port ${PORT}"]
