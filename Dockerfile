FROM python:3.11-slim

# Ishchi papka
WORKDIR /Faceid

# Sistem paketlari (agar kerak bo‘lsa)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libopencv-dev \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Requirements faylini konteynerga ko‘chirish
COPY requirements.txt /Faceid/

# Python paketlarini o‘rnatish
RUN pip install --upgrade pip setuptools wheel \
    && pip install --timeout=1200 --retries=10 --no-cache-dir -r requirements.txt

# Django statik va media papkalar
RUN mkdir -p /Faceid/staticfiles /Faceid/mediafiles

# Loyihani konteynerga ko‘chirish
COPY . /Faceid/

# Default komanda
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
