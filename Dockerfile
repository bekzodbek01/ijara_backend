
# Base image
FROM python:3.10

# Working directory
WORKDIR /Fac

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System dependencies (especially for dlib)
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

# Install Python dependencies
COPY requirements.txt /Fac/
RUN pip install --upgrade pip && pip install --default-timeout=300 --retries 20 --no-cache-dir -r requirements.txt

# Create static/media dirs
RUN mkdir -p /Fac/staticfiles /Faceid/mediafiles

# Copy project
COPY . /Fac/

# Collect static
RUN python manage.py collectstatic --noinput

# Django settings
ENV DJANGO_SETTINGS_MODULE=config.settings

# Expose port
EXPOSE 8000

# Run
#CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]




## Base image: Python 3.10
#FROM python:3.10-slim
#
## System dependencies
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    libpq-dev \
#    libgl1 \
#    libglib2.0-0 \
#    libsm6 \
#    libxrender1 \
#    libxext6 \
#    git \
#    && rm -rf /var/lib/apt/lists/*
#
## Workdir
#WORKDIR /app
#
## Copy requirements first
#COPY requirements.txt .
#
## Install Python packages
#RUN pip install --upgrade pip
#RUN pip install --no-cache-dir -r requirements.txt
#
## Copy project files
#COPY . .
#
## Environment variables
#ENV PYTHONUNBUFFERED=1
#
## Expose port
#EXPOSE 8000
#
## Start Django server
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
