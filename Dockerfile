# TensorFlow bazaviy imiji (CPU versiyasi)
FROM tensorflow/tensorflow:2.15.0-slim


# Ishchi katalog
WORKDIR /Fac

# Muhit o‘zgaruvchilar
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Sistem kutubxonalar (opencv, psycopg2 va boshqalar uchun kerak)
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

# Python kutubxonalarini o‘rnatish
COPY requirements.txt /Fac/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Statik fayllar uchun papkalar
RUN mkdir -p /Fac/staticfiles /Fac/mediafiles

# Loyiha fayllarini ko‘chirish
COPY . /Fac/

# Django sozlamalari
ENV DJANGO_SETTINGS_MODULE=config.settings

# Staticlarni tayyorlash
RUN python manage.py collectstatic --noinput || true

# Port ochish
EXPOSE 8000

# Gunicorn bilan ishga tushirish
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--threads=2", "--timeout=120"]
