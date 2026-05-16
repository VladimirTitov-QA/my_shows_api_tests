import os
import psycopg
import pytest
import requests
from dotenv import load_dotenv
from helpers.file_helpers import load_sql
from helpers.api_helpers import ApiSession
from config.api_config import BASE_URL

# Загружаем переменные окружения из файла .env.local
load_dotenv('.env.local')


@pytest.fixture(scope="session")
def api_session():
    """Фикстура для работы с API через ApiSession (с защитой от rate limiter и логированием в Allure)"""
    session = requests.Session()
    return ApiSession(session, base_url=BASE_URL)


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
def insert_series_from_file(db_connection, request):
    """Параметризованная фикстура вставляет данные из указанного SQL-файла.

    Параметр: имя SQL-файла в папке data/ (может быть None для случая 0 строк)
    Возвращает: количество сериалов в таблице после вставки

    Пример использования:
        @pytest.mark.parametrize("insert_series_from_file, expected_count", [
            (None, 0),
            ("insert_one_series.sql", 1),
            ("insert_three_series.sql", 3)
        ], indirect=["insert_series_from_file"])
        def test_example(self, insert_series_from_file, expected_count):
            assert insert_series_from_file == expected_count
    """

    # Проверяем наличие параметра (для случая 0 строк может быть None)
    if hasattr(request, 'param') and request.param is not None:
        sql_file = request.param  # Получаем имя SQL-файла из параметра
        body = load_sql(sql_file)  # Загружаем SQL из файла

        with db_connection.cursor() as cur:  # Создаём курсор для выполнения SQL-запросов
            cur.execute(body)  # Выполняем SQL-запрос
            db_connection.commit()  # Фиксируем изменения в базе данных
    else:
        # Для случая 0 строк — очищаем таблицу
        with db_connection.cursor() as cur:  # Создаём курсор для выполнения SQL-запросов
            # TRUNCATE - удаляет все строки из таблицы series
            # RESTART IDENTITY - сбрасывает счётчик id (начинает с 1)
            # CASCADE - удаляет зависимые данные (если есть)
            cur.execute("TRUNCATE series RESTART IDENTITY CASCADE;")  # Очищаем таблицу
            db_connection.commit()  # Фиксируем изменения в базе данных

    # Получаем количество сериалов в таблице
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM series;")
        count = cur.fetchone()[0]

    yield count  # Передаём количество в тест

    # Очищаем таблицу после теста
    with db_connection.cursor() as cur:  # Создаём курсор для выполнения SQL-запросов
        cur.execute("TRUNCATE series RESTART IDENTITY CASCADE;")  # Очищаем таблицу
        db_connection.commit()  # Фиксируем изменения в базе данных


@pytest.fixture(scope="function")
def insert_data_series(db_connection):
    """Фикстура вставляет тестовые данные в БД"""

    # load_sql() - читает SQL-запрос из файла data/insert_three_series.sql
    body = load_sql("insert_three_series.sql")

    with db_connection.cursor() as cur:  # Создаём курсор для выполнения SQL-запросов
        cur.execute(body)  # Выполняем SQL-запрос (вставка данных)
        db_connection.commit()  # Фиксируем изменения в базе данных

    yield  # Выполняем тест (данные уже вставлены)

    # Очищаем таблицу после теста
    with db_connection.cursor() as cur:  # Создаём курсор для выполнения SQL-запросов
        cur.execute("TRUNCATE series RESTART IDENTITY CASCADE;")  # Очищаем таблицу
        db_connection.commit()  # Фиксируем изменения в базе данных


@pytest.fixture(scope="function")
def create_single_series(db_connection):
    """Фикстура создаёт один тестовый сериал и возвращает его ID"""

    # load_sql() - читает SQL-запрос из файла data/insert_one_series_with_return_id.sql
    body = load_sql("insert_one_series_with_return_id.sql")

    with db_connection.cursor() as cur:  # Создаём курсор для выполнения SQL-запросов
        cur.execute(body)  # Выполняем SQL-запрос (вставка данных с RETURNING id)
        series_id = cur.fetchone()[0]  # Получаем ID созданного сериала из RETURNING
        db_connection.commit()  # Фиксируем изменения в базе данных

    yield series_id  # Передаём ID в тест (данные уже вставлены)

    # Очищаем таблицу после теста
    with db_connection.cursor() as cur:  # Создаём курсор для выполнения SQL-запросов
        cur.execute("DELETE FROM series WHERE id = %s;", (series_id,))  # Удаляем только этот созданный сериал по ID
        db_connection.commit()  # Фиксируем изменения в базе данных