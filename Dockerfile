FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg chromium chromium-driver fonts-liberation libglib2.0-0 libgl1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
COPY requirements.txt /opt/pixelmotion/requirements.txt
RUN pip install --upgrade pip && pip install -r /opt/pixelmotion/requirements.txt
COPY . /opt/pixelmotion

WORKDIR /opt/pixelmotion
EXPOSE 8000
CMD ["sh", "-c", "uvicorn pixelmotion.server.api_service:app --host 0.0.0.0 --port ${PORT:-8000}"]
