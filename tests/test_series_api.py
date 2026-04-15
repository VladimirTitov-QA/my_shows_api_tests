import allure
import pytest
from http import HTTPStatus
from jsonschema import validate
from config.api_config import SERIES_URL
from helpers.file_helpers import load_yaml


@allure.suite("Тесты на эндпоинт /series")
class TestGetSeries:

    @pytest.mark.positive  # ПРИМЕР: метка ПОЗИТИВНЫХ тестов из pytest.ini (запуск через: pytest -m positive)
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
    @allure.title("Получение списка сериалов при {expected_count} записях в БД")
    def test_get_series_returns_list(self, insert_series_from_file, api_session, expected_count):
        """Тест проверяет GET /series с разным количеством сериалов в БД"""

        # Получаем количество сериалов из фикстуры
        actual_count = insert_series_from_file

        with allure.step("Отправляем GET запрос на получение списка сериалов"):
            response = api_session.get(SERIES_URL)

        with allure.step("Проверяем статус код 200"):
            assert response.status_code == HTTPStatus.OK, f"Ожидался код 200, получен {response.status_code}"

        body = response.json()

        with allure.step("Проверяем JSON Schema (структура и типы)"):
            template = load_yaml("get_series_list.yml")
            validate(body, template)

        with allure.step(f"Проверяем количество сериалов: ожидается {expected_count}"):
            assert len(body) == expected_count, f"Ожидалось {expected_count} сериалов, получено {len(body)}"

        with allure.step("Проверяем соответствие с фикстурой"):
            assert actual_count == expected_count, \
                f"Фикстура вернула {actual_count}, ожидалось {expected_count}"

    @pytest.mark.negative  # ПРИМЕР: метка НЕГАТИВНЫХ тестов из pytest.ini (запуск через: pytest -v -m negative)
    @allure.title("Получение списка сериалов с невалидным параметром status")
    def test_get_series_with_invalid_status(self, insert_data_series, api_session):
        """Тест проверяет GET /series с невалидным значением status"""

        with allure.step("Отправляем GET запрос с невалидным параметром status=invalid_status"):
            response = api_session.get(SERIES_URL, params={"status": "invalid_status"})

        with allure.step("Проверяем статус код 400"):
            assert response.status_code == HTTPStatus.BAD_REQUEST, f"Ожидался код 400, получен {response.status_code}"

        body = response.json()

        with allure.step("Проверяем наличие описания ошибки в ответе"):
            assert "error" in body or "detail" in body, "В ответе отсутствует описание ошибки"


@allure.suite("Тесты на эндпоинт /series/{id}")
class TestUpdateSeries:

    @pytest.mark.positive  # ПРИМЕР: метка ПОЗИТИВНЫХ тестов из pytest.ini (запуск через: pytest -v -m positive)
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
    @allure.title("Обновление поля {param} сериала через PUT запрос")
    def test_update_series_single_field(self, create_single_series, db_connection, api_session, param, new_value):
        """Тест проверяет обновление отдельного поля сериала через PUT /api/v1/series/{id}"""

        series_id = create_single_series
        url = f"{SERIES_URL}/{series_id}"

        with allure.step(f"Получаем текущие обязательные поля (name, status) из БД для сериала ID {series_id}"):
            with db_connection.cursor() as cur:
                cur.execute("SELECT name, status FROM series WHERE id = %s;", (series_id,))
                current_name, current_status = cur.fetchone()

        # Формируем тело запроса
        update_payload = {
            "name": current_name,
            "status": current_status,
            param: new_value
        }

        with allure.step(f"Отправляем PUT запрос на обновление поля {param} на значение '{new_value}'"):
            response = api_session.put(url, json=update_payload)

        with allure.step("Проверяем статус код 200"):
            assert response.status_code == HTTPStatus.OK, f"Ожидался код 200, получен {response.status_code}"

        with allure.step("Проверяем ответ API"):
            response_body = response.json()
            assert response_body[param] == new_value, \
                f"Поле {param} в ответе ожидалось '{new_value}', получено '{response_body[param]}'"

        with allure.step("Проверяем обновление в базе данных"):
            with db_connection.cursor() as cur:
                cur.execute("SELECT name, photo, rating, status, review FROM series WHERE id = %s;", (series_id,))
                updated = cur.fetchone()

        field_index = {"name": 0, "photo": 1, "rating": 2, "status": 3, "review": 4}
        with allure.step(f"Проверяем, что поле {param} в БД обновилось на '{new_value}'"):
            assert updated[field_index[param]] == new_value, \
                f"В БД поле {param} ожидалось '{new_value}', получено '{updated[field_index[param]]}'"