import os
import psycopg
import pytest
from dotenv import load_dotenv
from helpers.file_helpers import load_sql

# Загружаем переменные окружения из файла .env
load_dotenv()


@pytest.fixture(scope="session")
def db_connection():
    """Фикстура подключения к БД (одна на всю сессию)"""

    with psycopg.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST")
    ) as conn:
        yield conn  # Передаём соединение в тест


@pytest.fixture(scope="function")
def insert_data_series(db_connection):
    """Фикстура вставляет тестовые данные в БД"""

    body = load_sql("insert_three_series.sql")  # load_sql() - читает SQL-запрос из файла data/insert_three_series.sql

    with db_connection.cursor() as cur:  # Создаём курсор для выполнения SQL-запросов
        cur.execute(body)  # Выполняем SQL-запрос (вставка данных)
        db_connection.commit()  # Фиксируем изменения в базе данных

    yield  # Выполняем тест (данные уже вставлены)

    # Очистка после теста
    with db_connection.cursor() as cur:  # Создаём курсор для выполнения SQL-запросов
        # TRUNCATE - удаляет все строки из таблицы series
        # RESTART IDENTITY - сбрасывает счётчик id (начинает с 1)
        # CASCADE - удаляет зависимые данные (если есть)
        cur.execute("TRUNCATE series RESTART IDENTITY CASCADE;")
        db_connection.commit()  # Фиксируем очистку