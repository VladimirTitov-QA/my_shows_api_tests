# Базовый образ: Python 3.14 (slim-версия для минимизации размера)
FROM python:3.14-slim

# Устанавливаем системные зависимости для psycopg2: libpq-dev и gcc нужны для сборки PostgreSQL-драйвера
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем /app как рабочую директорию для команд Dockerfile, которые следуют далее — здесь будет весь код проекта
WORKDIR /app

# Копируем файл requirements.txt с зависимостями (для кэширования слоя с зависимостями)
COPY requirements.txt .

# Устанавливаем зависимости (Python-пакеты) из requirements.txt без кэширования (экономия места)
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта
COPY . .

# Команда по умолчанию при запуске контейнера: запуск всех тестов pytest в подробном режиме
CMD ["pytest", "-v"]
