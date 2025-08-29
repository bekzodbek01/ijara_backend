# Base image
FROM python:3.10-slim

# Working directory
WORKDIR /Faceid

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=300

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    libpq-dev \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install light packages first
COPY light-packages.txt /Faceid/
RUN pip install --upgrade pip setuptools wheel \
    && pip install --retries 10 --timeout 300 --no-cache-dir -r light-packages.txt

# Copy and install heavy packages (TensorFlow, dlib, face-recognition, etc.)
COPY heavy-packages.txt /Faceid/
RUN pip install --retries 10 --timeout 600 --no-cache-dir -r heavy-packages.txt

# Create static and media directories
RUN mkdir -p /Faceid/staticfiles /Faceid/mediafiles

# Copy project files
COPY . /Faceid/

# Django settings
ENV DJANGO_SETTINGS_MODULE=config.settings

# Expose Django port
EXPOSE 8000

# Run migrations, collectstatic, and start server
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
