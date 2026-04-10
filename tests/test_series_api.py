import pytest
import requests
from http import HTTPStatus
from jsonschema import validate
from config.api_config import SERIES_URL
from helpers.file_helpers import load_yaml


class TestGetSeries:
    """Тесты для GET /api/v1/series"""

    @pytest.mark.positive
    # Тест: Получение списка сериалов
    def test_get_series_returns_list(self, insert_data_series):
        """Тест проверяет, что GET /series возвращает список сериалов"""

        response = requests.get(SERIES_URL)

        # Проверка статус кода ответа
        assert response.status_code == HTTPStatus.OK, f"Ожидался код 200, получен {response.status_code}"
        body = response.json()

        # Проверяем JSON Schema (структура и типы)
        template = load_yaml("get_series_list.yml")
        validate(body, template)

        # Проверка количества сериалов
        assert len(body) == 2, f"Ожидалось 2 сериала, получено {len(body)}"

    @pytest.mark.negative
    # Тест: Получение списка сериалов с некорректным статусом
    def test_get_series_with_invalid_status(self, insert_data_series):
        """Тест проверяет GET /series с некорректным значением status"""

        response = requests.get(SERIES_URL, params={"status": "invalid_status"})

        # Проверка статус кода ответа
        assert response.status_code == HTTPStatus.BAD_REQUEST, f"Ожидался код 400, получен {response.status_code}"
        body = response.json()

        # Проверка наличия описания ошибки
        assert "error" in body or "detail" in body, "В ответе отсутствует описание ошибки"