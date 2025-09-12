# Base image
FROM python:3.10-slim-bullseye

# Working directory
WORKDIR /Fac

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# System dependencies (minimum kerakli kutubxonalar)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pip packages (bir qatorda install qilish tezroq bo‘ladi)
COPY requirements.txt /Fac/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Static/media folders
RUN mkdir -p /Fac/staticfiles /Fac/mediafiles

# Copy project
COPY . /Fac/

# Django settings
ENV DJANGO_SETTINGS_MODULE=config.settings

# Collect static files (staticlarni container ichida tayyorlab qo‘yish)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# CMD: run with gunicorn (production)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--threads=2", "--timeout=120"]
