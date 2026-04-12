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
│ ├── api_helpers.py # ApiSession с обработкой rate limiter
│ └── file_helpers.py # Вспомогательные функции (загрузка SQL/YAML)
│
├── schemas/
│ └── get_series_list.yml # JSON Schema для валидации ответа
│
├── tests/
│ └── test_series_api.py # Тесты для GET и PUT /api/v1/series
│
├── .env # Переменные окружения (данные для БД)
├── .gitignore # Исключения для Git
├── conftest.py # Подключение фикстур для pytest
├── pytest.ini # Настройки и маркеры pytest
├── README.md # Описание проекта
└── requirements.txt # Зависимости проекта
```

## Пояснения

### Фикстуры
- **`api_session`** — сессия для работы с API с автоматической обработкой rate limiter (повторные попытки 
при превышении лимита запросов).
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
- 
#### PUT `/api/v1/series/{id}`
- **`test_update_series_single_field`** — параметризованный позитивный тест. Проверяет обновление 
каждого из 5 полей сериала: `name`, `photo`, `rating`, `status`, `review`. Для каждого поля выполняется отдельный тест 
с проверкой ответа API и состояния базы данных.

### Прочее
- **JSON Schema валидация** через YAML-файлы обеспечивает строгую проверку структуры и типов данных ответа API.
- **Маркеры `positive` / `negative`** позволяют запускать тесты группами без дублирования кода.
- **Разделение на `config/`, `data/`, `fixtures/`, `helpers/`, `schemas/`** обеспечивает чистое разделение 
ответственности, упрощая поддержку и масштабирование проекта.
- **Файл `.env`** хранит параметры подключения к БД и не попадает в Git, что безопасно.

## Запуск тестов
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

## Требования
- Python 3.14+
- Docker и Docker Compose (для запуска тестируемого сервиса My Shows)
- Установленные зависимости из `requirements.txt`
- Файл `.env` с переменными подключения к БД:

```
POSTGRES_DB=my-shows-rating
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD="смотри в ТЗ"
```

## Предварительные шаги
1. Запустить сервис My Shows локально через Docker Compose
2. Убедиться, что база данных доступна по указанным в `.env` параметрам

#### Проект выполнен в рамках учебной программы по автоматизации тестирования API

---
**В этом файле используется верстка [Markdown](https://www.markdownguide.org/basic-syntax/)**