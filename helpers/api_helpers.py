import time
from http import HTTPStatus

from requests import Session


class ApiSession:
    """Класс-обёртка для requests.Session с обработкой rate limiter'a.

    При получении ответа с кодом 400 и сообщением "Лимит запросов превышен"
    автоматически делает повторные попытки в течение 5 секунд.
    """

    def __init__(self, session: Session):
        """Инициализация с переданной сессией requests."""
        self.session = session

    def _send(self, method: str, url: str, **kwargs):
        """Внутренний метод для отправки запросов с retry-логикой."""
        timestamp = time.time() + 5  # Устанавливаем таймаут 5 секунд

        while time.time() < timestamp:
            response = self.session.request(method=method, url=url, **kwargs)
            response_body = response.json()

            # Если rate limiter сработал — ждём 1 секунду и повторяем
            if (response.status_code == HTTPStatus.BAD_REQUEST and
                    response_body.get("message") == "Лимит запросов превышен"):
                time.sleep(1)
            else:
                break
        else:
            # Если за 5 секунд так и не удалось обойти rate limiter
            raise AssertionError("Не удалось прорваться через rate limiter")

        return response

    def get(self, url: str, params: dict | None = None):
        """GET-запрос с обработкой rate limiter'a."""
        return self._send("GET", url=url, params=params)

    def post(self, url: str, params: dict | None = None, json: dict | None = None):
        """POST-запрос с обработкой rate limiter'a."""
        return self._send("POST", url=url, params=params, json=json)

    def put(self, url: str, params: dict | None = None, json: dict | None = None):
        """PUT-запрос с обработкой rate limiter'a."""
        return self._send("PUT", url=url, params=params, json=json)

    def patch(self, url: str, params: dict | None = None, json: dict | None = None):
        """PATCH-запрос с обработкой rate limiter'a."""
        return self._send("PATCH", url=url, params=params, json=json)

    def delete(self, url: str, params: dict | None = None):
        """DELETE-запрос с обработкой rate limiter'a."""
        return self._send("DELETE", url=url, params=params)