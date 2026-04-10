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
│ └── insert_three_series.sql # SQL-скрипт с тестовыми данными
│
├── fixtures/
│ └── api_fixtures.py # Фикстуры для работы с БД
│
├── helpers/
│ └── file_helpers.py # Вспомогательные функции (загрузка SQL/YAML)
│
├── schemas/
│ └── get_series_list.yml # JSON Schema для валидации ответа
│
├── tests/
│ └── test_series_api.py # Тесты для GET /api/v1/series
│
├── .env # Переменные окружения (данные для БД)
├── .gitignore # Исключения для Git
├── conftest.py # Подключение фикстур для pytest
├── pytest.ini # Настройки и маркеры pytest
├── README.md # Описание проекта
└── requirements.txt # Зависимости проекта
```

## Пояснения

- **Фикстура `db_connection`** создаёт подключение к PostgreSQL и автоматически закрывает его после завершения сессии тестов.
- **Фикстура `insert_data_series`** загружает тестовые данные из SQL-файла перед тестом и очищает таблицу `series` после теста.
- **JSON Schema валидация** через YAML-файлы обеспечивает строгую проверку структуры и типов данных ответа API.
- **Маркеры `positive` / `negative`** позволяют запускать тесты группами без дублирования кода.
- **Разделение на `config/`, `data/`, `fixtures/`, `helpers/`, `schemas/`** обеспечивает чистое разделение ответственности, упрощая поддержку и масштабирование проекта.
- **Файл` .env`** хранит параметры подключения к БД и не попадает в Git, что безопасно.

## Запуск тестов

```bash
# Запуск всех тестов
pytest -v

# Запуск только позитивных тестов
pytest -m positive -v

# Запуск только негативных тестов
pytest -m negative -v
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