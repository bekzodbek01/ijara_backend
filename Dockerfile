# Base image
FROM python:3.10-slim-bullseye

# Working directory
WORKDIR /Fac

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/Fac/.venv/bin:$PATH"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libopencv-dev \
    python3-opencv \
    wget \
    curl \
    unzip \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Virtual environment yaratish
RUN python -m venv /Fac/.venv

# Upgrade pip & o‘rnatish
COPY requirements.txt /Fac/
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Static/media folders
RUN mkdir -p /Fac/staticfiles /Fac/mediafiles

# Copy project
COPY . /Fac/

# Django settings
ENV DJANGO_SETTINGS_MODULE=config.settings

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# CMD: run with gunicorn (virtual environment ishlatadi)
CMD ["/Fac/.venv/bin/gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--threads=2", "--timeout=120"]
