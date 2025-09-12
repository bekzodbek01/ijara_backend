# Base image
FROM python:3.10-slim-bullseye

# Working directory
WORKDIR /Fac

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install pip packages
COPY requirements.txt /Fac/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Static/media folders
RUN mkdir -p /Fac/staticfiles /Fac/mediafiles

# Copy project
COPY . /Fac/

# Django settings
ENV DJANGO_SETTINGS_MODULE=config.settings

# Expose port
EXPOSE 8000

# CMD: run with gunicorn (production)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3"]
