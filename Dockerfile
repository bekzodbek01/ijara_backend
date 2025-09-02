# Python 3.10 slim ishlatamiz
FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Requirementsni copy qilamiz va o'rnatamiz
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Project fayllarini copy qilamiz
COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Django serverni ishga tushiramiz
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
