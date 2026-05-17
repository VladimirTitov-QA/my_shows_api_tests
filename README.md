# MyShowsAPITests

Тестовый проект для автоматизации тестирования API сервиса My Shows (сервис для ведения рейтинга сериалов).

## Структура проекта
```
myshows_api_tests/
│
├── config/
│ └── api_config.py # URL-ы API эндпоинтов
│
├── data/
│ ├── insert_one_series.sql # SQL для вставки 1 сериала (GET тесты)
│ ├── insert_one_series_with_return_id.sql # SQL для вставки 1 сериала с RETURNING id (PUT тесты)
│ └── insert_three_series.sql # SQL для вставки 3 сериалов
│
├── fixtures/
│ └── api_fixtures.py # Фикстуры для работы с БД и API
│
├── helpers/
│ ├── api_helpers.py # ApiSession с обработкой rate limiter и логированием в Allure
│ └── file_helpers.py # Вспомогательные функции (загрузка SQL/YAML)
│
├── schemas/
│ └── get_series_list.yml # JSON Schema для валидации ответа
│
├── tests/
│ └── test_series_api.py # Тесты для GET и PUT /api/v1/series
│
├── .env # Переменные окружения для работы приложения (не попадает в Git)
├── .env.local # Переменные окружения для локального запуска тестов (не попадает в Git)
├── .gitignore # Исключения для Git
├── conftest.py # Подключение фикстур для pytest
├── docker-compose.yml # Запуск приложения + тестов через Docker Compose
├── Dockerfile # Инструкции для сборки Docker образа с тестами
├── pytest.ini # Настройки и маркеры pytest
├── README.md # Описание проекта
└── requirements.txt # Зависимости проекта
```

## Пояснения

### Фикстуры
- **`api_session`** — сессия для работы с API с автоматической обработкой rate limiter и логированием в Allure.
- **`db_connection`** — подключение к PostgreSQL, автоматически закрывается после завершения сессии тестов.
- **`insert_series_from_file`** — параметризованная фикстура, вставляет данные из указанного SQL-файла. 
  Для случая 0 строк принимает `None` и просто очищает таблицу. Возвращает количество сериалов в БД.
- **`insert_data_series`** — фикстура для вставки 3 тестовых сериалов (используется в негативном тесте).
- **`create_single_series`** — фикстура создаёт один сериал и возвращает его ID (используется в PUT тестах).

### Тесты

#### GET `/api/v1/series`
- **`test_get_series_returns_list`** — параметризованный позитивный тест. Проверяет ответ API при разном 
  количестве сериалов в БД: 0, 1 и 3. Валидирует JSON Schema и количество записей.
- **`test_get_series_with_invalid_status`** — негативный тест. Проверяет, что при передаче некорректного статуса 
  API возвращает ошибку 400.

#### PUT `/api/v1/series/{id}`
- **`test_update_series_single_field`** — параметризованный позитивный тест. Проверяет обновление 
  каждого из 5 полей сериала: `name`, `photo`, `rating`, `status`, `review`. Для каждого поля выполняется отдельный тест 
  с проверкой ответа API и состояния базы данных.

### Allure-отчёты
- **Класс `ApiSession`** автоматически логирует все запросы и ответы в Allure-отчёт.
- **Все тесты** обёрнуты в `@allure.suite`, `@allure.title` и `with allure.step()` для детализации шагов.
- **Allure-результаты** сохраняются в папку `allure-results` при каждом запуске тестов.

### Прочее
- **JSON Schema валидация** через YAML-файлы обеспечивает строгую проверку структуры и типов данных ответа API.
- **Маркеры `positive` / `negative`** позволяют запускать тесты группами без дублирования кода.
- **Разделение на `config/`, `data/`, `fixtures/`, `helpers/`, `schemas/`** обеспечивает чистое разделение 
  ответственности, упрощая поддержку и масштабирование проекта.
- **Файл `.env`** хранит параметры подключения к БД и не попадает в Git, что безопасно.
- **Файл `.env.local`** используется для локального запуска тестов (вне Docker). 
  В нём задаётся `POSTGRES_HOST=localhost` и другие параметры. Загружается в `api_fixtures.py` через `load_dotenv('.env.local')`.
- **`config/api_config.py`** теперь читает переменную `API_BASE_URL` (значение по умолчанию `http://localhost/api/v1`). 
  Благодаря этому тесты могут работать как локально, так и внутри Docker, где через `docker-compose.yml` 
  передаётся `API_BASE_URL=http://msr-backend:8000/api/v1`.

### Dockerfile
- **Dockerfile** — файл для сборки Docker-образа с тестами. В нём:
  - Устанавливаются системные зависимости (`libpq-dev`, `gcc`), необходимые для `psycopg2`.
  - Копируется код проекта и устанавливаются Python-зависимости из `requirements.txt`.
  - Команда по умолчанию — `pytest -v`.

### Docker Compose
- **`docker-compose.yml`** описывает три сервиса: `msr-db`, `msr-backend` и `api-tests`.
- Тесты зависят от здоровья бэкенда (`condition: service_healthy`), 
  подключаются к API через `API_BASE_URL=http://msr-backend:8000/api/v1`, а к БД через `POSTGRES_HOST=msr-db`.
- Для запуска достаточно выполнить `docker-compose up --build` из папки проекта.

## Запуск тестов локально
```bash
# Запуск всех тестов
pytest -v

# Запуск только позитивных тестов
pytest -m positive -v

# Запуск только негативных тестов
pytest -m negative -v

# Запуск конкретного тестового класса
pytest -v tests/test_series_api.py::TestGetSeries

# Запуск параметризованного теста с конкретным параметром
pytest -v tests/test_series_api.py::TestGetSeries::test_get_series_returns_list[zero_series]
```

## Генерация Allure-отчёта после запуска тестов локально
```bash
# 1. Запустить тесты (результаты сохранятся в allure-results)
pytest -v

# 2. Сгенерировать единый HTML-отчёт
allure generate allure-results -o allure-report --clean --single-file

# 3. Открыть отчёт для просмотра
allure open allure-report
```

## Запуск тестов через Docker (сборка образа и ручной запуск)
```bash
# Сборка образа
docker build -t myshows-api-tests:v1 .

# Просмотр списка тестов (без выполнения)
docker run --rm myshows-api-tests:v1 pytest --collect-only

# Запуск всех тестов (требуется работающее приложение и БД)
docker run --rm --network host myshows-api-tests:v1 pytest -v
```

## Запуск тестов через Docker Compose (запуск приложения и тестов в одной сети)
```bash
# Сборка и запуск всех сервисов (приложение + тесты)
docker-compose up --build

# Сборка и запуск всех сервисов (приложение + тесты) в фоновом режиме
docker-compose up -d --build

# Просмотр логов тестов
docker-compose logs api-tests

# Просмотр логов всех сервисов в реальном времени
docker-compose logs -f

# Остановка и удаление всех контейнеров
docker-compose down
```
**Примечание:** тесты запускаются автоматически после готовности бэкенда. Контейнер с тестами завершится (exit 0), 
а приложение останется работать. Результаты Allure сохраняются в папку `./allure-results` на хосте 
(благодаря смонтированному тому). Для повторного прогона тестов снова выполнить `docker-compose up --build`.

## Генерация Allure-отчёта после запуска тестов через Docker Compose
```bash
# 1. Запустить тесты через Docker Compose (результаты сохранятся в ./allure-results)
docker-compose up --build

# 2. Сгенерировать единый HTML-отчёт из результатов, полученных в Docker
allure generate allure-results -o allure-report --clean --single-file

# 3. Открыть отчёт для просмотра
allure open allure-report
```
**Примечание:** папка `allure-results` монтируется в контейнер и появляется на хосте после выполнения тестов. 
Она уже добавлена в `.gitignore`.

## Требования
- Python 3.14+
- Docker и Docker Compose (для запуска тестируемого сервиса My Shows)
- Установленные зависимости из `requirements.txt`
- Allure Report (установленный локально)
- Файл `.env.local` с переменными подключения к БД (для локального запуска тестов, 
  не обязателен, если тесты запускаются только через Docker):
```
POSTGRES_DB=my-shows-rating
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123456
```
- Файл `.env` с содержимым (для Docker-приложения,
  не обязателен, если тесты запускаются только локально):
```
PROJECT_NAME=QAS-MSR
ENV=prod

PORT=8000
CORS_ORIGINS_STRING='http://127.0.0.1 http://127.0.0.1:3000'

POSTGRES_DB=my-shows-rating
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123456
POSTGRES_HOST=msr-db
POSTGRES_PORT=5432
POSTGRES_PATH=${POSTGRES_DB}
POSTGRES_DSN=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_PATH}

HOST=0.0.0.0
FRONTEND_PORT=3000
ORIGIN=http://127.0.0.1
XFF_DEPTH=2
ADDRESS_HEADER=X-Forwarded-For
PROTOCOL_HEADER=X-Forwarded-Proto
HOST_HEADER=X-Forwarded-Host
SERVERDEV=false
```

## Предварительные шаги

### Для локального запуска тестов (без Docker)
1. Запустить приложение **My Shows Rating** (`my-shows-rating`) локально через Docker Compose.
2. Создать в корне проекта **My Shows Api Tests** (`myshows_api_tests`) файл `.env.local`
   (пример содержимого см. в разделе **Требования**).
3. Убедиться, что PostgreSQL запущен на `localhost:5432`, база `my-shows-rating` создана, 
   а параметры подключения совпадают с указанными в `.env.local`.
4. Установить зависимости: `pip install -r requirements.txt`.
5. Установить Allure Report (CLI-инструмент) – не входит в `requirements.txt`, 
   необходим для генерации Allure-отчёта (HTML-отчёта) из результатов тестов.

### Для запуска тестов через Docker Compose
1. Создать в корне проекта **My Shows Api Tests** (`myshows_api_tests`) файл `.env`
   (пример содержимого см. в разделе **Требования**).

2. Запустить docker compose
```bash
docker-compose up -d --build
```

#### Проект выполнен в рамках учебной программы по автоматизации тестирования API

---
**В этом файле используется верстка [Markdown](https://www.markdownguide.org/basic-syntax/)**
