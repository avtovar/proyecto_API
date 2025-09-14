import os
import random
import string
import requests
import pytest
import faker
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

# URL base de la API
BASE_URL = os.getenv("BASE_URL", "https://cf-automation-airline-api.onrender.com")
AUTH_LOGIN = "/auth/login/"
AIRPORT = "/airports/"
fake = faker.Faker()

# Configuración de reintentos y timeouts
REQUEST_TIMEOUT = 15  # Aumentar timeout a 15 segundos
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.5


@pytest.fixture(scope="session")
def base_url():
    """Fixture que retorna la URL base de la API"""
    return BASE_URL


@pytest.fixture(scope="session")
def session_with_retries():
    """Crear una sesión con reintentos"""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


@pytest.fixture(scope="session")
def admin_token(session_with_retries) -> str:
    """Fixture para obtener token de administrador con reintentos"""
    user = os.getenv("ADMIN_USER", "admin@demo.com")
    pwd = os.getenv("ADMIN_PASS", "admin123")

    url = BASE_URL + AUTH_LOGIN
    print(f"Attempting to login to: {url}")

    try:
        r = session_with_retries.post(
            url,
            data={
                "grant_type": "",
                "username": user,
                "password": pwd,
                "scope": "",
                "client_id": "",
                "client_secret": ""
            },
            headers={
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=REQUEST_TIMEOUT
        )

        if r.status_code != 200:
            raise RuntimeError(f"Login failed ({r.status_code}): {r.text}")

        return r.json()["access_token"]
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error connecting to API: {str(e)}")


@pytest.fixture
def auth_headers(admin_token):
    """Fixture que retorna headers de autenticación"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def airport(auth_headers, session_with_retries):
    """Fixture para crear un aeropuerto temporal para pruebas"""
    airport_data = {
        "iata_code": "".join(random.choices(string.ascii_uppercase, k=3)),
        "city": "La Paz",
        "country": fake.country_code()
    }

    try:
        r = session_with_retries.post(
            BASE_URL + AIRPORT,
            json=airport_data,
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()
        airport_response = r.json()

        yield airport_response

        # Cleanup: eliminar el aeropuerto después de la prueba
        try:
            session_with_retries.delete(
                BASE_URL + AIRPORT + f'{airport_response["iata_code"]}',
                headers=auth_headers,
                timeout=REQUEST_TIMEOUT
            )
        except requests.exceptions.RequestException:
            # Si falla el cleanup, continuar de todos modos
            pass
    except requests.exceptions.RequestException as e:
        pytest.skip(f"API no disponible: {str(e)}")