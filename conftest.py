import os
import random
import string
import requests
import pytest
import faker
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Cargar variables de entorno
load_dotenv()

# Obtener variables de entorno con valores por defecto
BASE_URL = os.getenv("BASE_URL", "https://cf-automation-airline-api.onrender.com")
AUTH_LOGIN = "/auth/login/"
AIRPORT = "/airports/"
fake = faker.Faker()

# Configuración de reintentos y timeouts
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.5



@pytest.fixture(scope="session")
def base_url():
    """Fixture que retorna la URL base de la API"""
    return BASE_URL


@pytest.fixture(scope="session")
def check_api_availability():
    """Fixture para verificar que la API está disponible"""
    import os
    base_url = os.getenv("BASE_URL")
    if not base_url:
        pytest.fail("BASE_URL no está configurada")

    # Intentar una conexión simple a la API
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            pytest.skip(f"API no disponible (status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        pytest.skip(f"API no disponible: {str(e)}")


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