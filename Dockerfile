# Base image
FROM python:3.10-slim

# Working directory
WORKDIR /Faceid

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=1200

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

# Copy requirements
COPY requirements.txt /Faceid/

# Install Python packages
RUN pip install --upgrade pip setuptools wheel \
    && pip install --timeout=1200 --retries=10 --no-cache-dir -r requirements.txt

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
