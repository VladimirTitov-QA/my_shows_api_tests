import json
import time
from http import HTTPStatus

import allure
from requests import Session


class ApiSession:
    """Класс-обёртка для requests.Session с обработкой rate limiter'a и логированием в Allure.

    При получении ответа с кодом 400 и сообщением "Лимит запросов превышен"
    автоматически делает повторные попытки в течение 5 секунд.
    """

    def __init__(self, session: Session, base_url: str = ""):
        """Инициализация с переданной сессией requests и базовым URL."""
        self.session = session
        self.base_url = base_url.rstrip("/")

    def _build_url(self, url: str) -> str:
        """Формирует полный URL на основе базового."""
        if url.startswith("http://") or url.startswith("https://"):
            return url
        url = url.lstrip("/")
        return f"{self.base_url}/{url}"

    def _send(self, method: str, url: str, **kwargs):
        """Внутренний метод для отправки запросов с retry-логикой и логированием."""
        full_url = self._build_url(url)
        timestamp = time.time() + 5  # Устанавливаем таймаут 5 секунд

        while time.time() < timestamp:
            response = self.session.request(method=method, url=full_url, **kwargs)

            # Логирование запроса и ответа в Allure
            if isinstance(response.request.body, bytes):
                body = response.request.body.decode(encoding="utf-8")
            else:
                body = response.request.body

            # Обработка ответа (на случай если это не JSON)
            try:
                response_json = response.json()
                response_body_for_log = json.dumps(response_json, indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                response_json = None
                response_body_for_log = response.text or ""

            allure.attach(
                body=f"Request:\n"
                     f"URL: {response.request.url}\n"
                     f"Headers: {json.dumps(dict(response.request.headers), indent=4, ensure_ascii=False)}\n"
                     f"Body: {json.dumps(body, indent=4, ensure_ascii=False)}\n\n"
                     f"Response:\n"
                     f"Status code: {response.status_code}\n"
                     f"Headers: {json.dumps(dict(response.headers), indent=4, ensure_ascii=False)}\n"
                     f"Body: {response_body_for_log}\n",
                name="Детальная информация о запросе и ответе",
                attachment_type=allure.attachment_type.TEXT,
            )

            # Проверка rate limiter'а
            if response_json is not None:
                if (response.status_code == HTTPStatus.BAD_REQUEST and
                        response_json.get("message") == "Лимит запросов превышен"):
                    time.sleep(1)
                    continue

            return response

        # Если за 5 секунд так и не удалось обойти rate limiter
        raise AssertionError("Не удалось прорваться через rate limiter")

    @allure.step("GET-запрос к адресу {url}")
    def get(self, url: str, params: dict | None = None, headers: dict | None = None):
        """GET-запрос с обработкой rate limiter'a и логированием."""
        return self._send("GET", url=url, params=params, headers=headers)

    @allure.step("POST-запрос к адресу {url}")
    def post(self, url: str, params: dict | None = None, json: dict | None = None, headers: dict | None = None):
        """POST-запрос с обработкой rate limiter'a и логированием."""
        return self._send("POST", url=url, params=params, json=json, headers=headers)

    @allure.step("PUT-запрос к адресу {url}")
    def put(self, url: str, params: dict | None = None, json: dict | None = None, headers: dict | None = None):
        """PUT-запрос с обработкой rate limiter'a и логированием."""
        return self._send("PUT", url=url, params=params, json=json, headers=headers)

    @allure.step("PATCH-запрос к адресу {url}")
    def patch(self, url: str, params: dict | None = None, json: dict | None = None, headers: dict | None = None):
        """PATCH-запрос с обработкой rate limiter'a и логированием."""
        return self._send("PATCH", url=url, params=params, json=json, headers=headers)

    @allure.step("DELETE-запрос к адресу {url}")
    def delete(self, url: str, params: dict | None = None, headers: dict | None = None):
        """DELETE-запрос с обработкой rate limiter'a и логированием."""
        return self._send("DELETE", url=url, params=params, headers=headers)