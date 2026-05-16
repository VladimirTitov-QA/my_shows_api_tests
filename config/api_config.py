import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost/api/v1")
SERIES_URL = f"{BASE_URL}/series"
SERIES_HACK_SERVER_URL = f"{BASE_URL}/series/hack_server"