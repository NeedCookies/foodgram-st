# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем setuptools
RUN pip install --no-cache-dir setuptools

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . /app/

# Указываем порт
EXPOSE 8000

# Запускаем сервер
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]