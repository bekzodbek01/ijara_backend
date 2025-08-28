# Base image
FROM python:3.10

# Working directory
WORKDIR /Faceid

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# System dependencies (for dlib, psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /Faceid/
RUN pip install --upgrade pip setuptools wheel \
    && pip install --default-timeout=300 --retries 20 --no-cache-dir -r requirements.txt

# Create static/media dirs
RUN mkdir -p /Faceid/staticfiles /Faceid/mediafiles

# Copy project files
COPY . /Faceid/

# Django settings
ENV DJANGO_SETTINGS_MODULE=config.settings

# Expose Django port
EXPOSE 8000

# Run migrations + collectstatic at container start
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
