# Base image
FROM python:3.10

# Working directory
WORKDIR /Faceid

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
COPY requirements.txt /Faceid/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Create static/media dirs
RUN mkdir -p /Faceid/staticfiles /Faceid/mediafiles

# Copy project
COPY . /Faceid/

# Collect static
RUN python manage.py collectstatic --noinput

# Django settings
ENV DJANGO_SETTINGS_MODULE=config.settings

# Expose port
EXPOSE 8000

# Run
#CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
