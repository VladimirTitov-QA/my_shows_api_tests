import pytest
from http import HTTPStatus
from jsonschema import validate
from config.api_config import SERIES_URL
from helpers.file_helpers import load_yaml


class TestGetSeries:
    """Тесты для GET /api/v1/series"""

    @pytest.mark.positive
    @pytest.mark.parametrize(
        "insert_series_from_file, expected_count",
        [
            (None, 0),
            ("insert_one_series.sql", 1),
            ("insert_three_series.sql", 3),
        ],
        ids=[
            "zero_series",
            "one_series",
            "three_series"
        ],
        indirect=["insert_series_from_file"]
    )
    def test_get_series_returns_list(self, insert_series_from_file, api_session, expected_count):
        """Тест проверяет GET /series с разным количеством сериалов в БД"""

        # Получаем количество сериалов из фикстуры
        actual_count = insert_series_from_file

        # Выполняем GET-запрос
        response = api_session.get(SERIES_URL)

        # Проверяем статус код ответа
        assert response.status_code == HTTPStatus.OK, f"Ожидался код 200, получен {response.status_code}"

        body = response.json()

        # Проверяем JSON Schema
        template = load_yaml("get_series_list.yml")
        validate(body, template)

        # Проверяем количество сериалов
        assert len(body) == expected_count, f"Ожидалось {expected_count} сериалов, получено {len(body)}"

        # Проверяем соответствие с фикстурой
        assert actual_count == expected_count, \
            f"Фикстура вернула {actual_count}, ожидалось {expected_count}"

    @pytest.mark.negative
    def test_get_series_with_invalid_status(self, insert_data_series, api_session):
        """Тест проверяет GET /series с некорректным значением status"""

        # Выполняем GET-запрос с некорректным статусом
        response = api_session.get(SERIES_URL, params={"status": "invalid_status"})

        # Проверяем статус код ответа
        assert response.status_code == HTTPStatus.BAD_REQUEST, f"Ожидался код 400, получен {response.status_code}"

        body = response.json()

        # Проверяем наличие описания ошибки
        assert "error" in body or "detail" in body, "В ответе отсутствует описание ошибки"


class TestUpdateSeries:
    """Тесты для PUT /api/v1/series/{id}"""

    @pytest.mark.positive
    @pytest.mark.parametrize(
        "param, new_value",
        [
            ("name", "Обновлённые Пацаны"),
            ("photo", "https://example.com/updated_photo.jpg"),
            ("rating", 10),
            ("status", "will_watch"),
            ("review", "Пересмотрел ещё раз, всё ещё отлично!"),
        ],
        ids=[
            "update_name",
            "update_photo",
            "update_rating",
            "update_status",
            "update_review"
        ]
    )
    def test_update_series_single_field(self, create_single_series, db_connection, api_session, param, new_value):
        """Тест проверяет обновление отдельного поля сериала через PUT /api/v1/series/{id}"""

        series_id = create_single_series
        url = f"{SERIES_URL}/{series_id}"

        # Получаем текущие обязательные поля из БД
        with db_connection.cursor() as cur:
            cur.execute("SELECT name, status FROM series WHERE id = %s;", (series_id,))
            current_name, current_status = cur.fetchone()

        # Формируем тело запроса
        update_payload = {
            "name": current_name,
            "status": current_status,
            param: new_value
        }

        # Выполняем PUT-запрос
        response = api_session.put(url, json=update_payload)

        # Проверяем статус код ответа
        assert response.status_code == HTTPStatus.OK, f"Ожидался код 200, получен {response.status_code}"

        # Проверяем ответ API
        response_body = response.json()
        assert response_body[param] == new_value, \
            f"Поле {param} в ответе ожидалось '{new_value}', получено '{response_body[param]}'"

        # Проверяем БД
        with db_connection.cursor() as cur:
            cur.execute("SELECT name, photo, rating, status, review FROM series WHERE id = %s;", (series_id,))
            updated = cur.fetchone()

        field_index = {"name": 0, "photo": 1, "rating": 2, "status": 3, "review": 4}
        assert updated[field_index[param]] == new_value, \
            f"В БД поле {param} ожидалось '{new_value}', получено '{updated[field_index[param]]}'"