import os
import random
import string
import requests
import pytest
import faker
import sys
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Añadir el directorio raíz del proyecto al path de Python para importar api_client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar el cliente API unificado
from api_client import APIClient, LOGIN_SCHEMA, ERROR_SCHEMA, SUCCESS_SCHEMA

# Cargar variables de entorno
load_dotenv()

# Configuración base de la API
BASE_URL = os.getenv("BASE_URL", "https://cf-automation-airline-api.onrender.com")
AUTH_LOGIN = "/auth/login/"
AIRPORT = "/airports/"
fake = faker.Faker()

# Configuración de reintentos y timeouts
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.5


@pytest.fixture(scope="session")
def session_with_retries():
    """Crea una sesión HTTP con reintentos automáticos."""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


@pytest.fixture(scope="session")
def base_url():
    """Retorna la URL base de la API."""
    return BASE_URL


@pytest.fixture(scope="session")
def admin_token(session_with_retries) -> str:
    """Obtiene token de administrador con reintentos y validación de errores."""
    user = os.getenv("ADMIN_USER", "admin@demo.com")
    pwd = os.getenv("ADMIN_PASS", "admin123")

    url = BASE_URL + AUTH_LOGIN
    print(f"[conftest] Intentando login en: {url}")

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
        r.raise_for_status()
        return r.json().get("access_token")
    except requests.exceptions.RequestException as e:
        pytest.exit(f"❌ Error conectando a la API: {str(e)}")
    except KeyError:
        pytest.exit(f"❌ Error: respuesta de login inválida → {r.text}")


@pytest.fixture
def auth_headers(admin_token):
    """Retorna headers de autenticación con Bearer token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def airport(auth_headers, session_with_retries):
    """Crea un aeropuerto temporal para pruebas y lo elimina al finalizar."""
    airport_data = {
        "iata_code": "".join(random.choices(string.ascii_uppercase, k=3)),
        "city": "La Paz",
        "country": fake.country()  # Usar nombre completo del país
    }

    try:
        r = session_with_retries.post(
            BASE_URL + AIRPORT,
            json=airport_data,
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT
        )
        if r.status_code == 400:
            pytest.skip(f"No se pudo crear aeropuerto de prueba: {r.text}")
        r.raise_for_status()
        airport_response = r.json()

        yield airport_response  # Se entrega al test

    finally:
        try:
            session_with_retries.delete(
                BASE_URL + AIRPORT + f'{airport_data["iata_code"]}',
                headers=auth_headers,
                timeout=REQUEST_TIMEOUT
            )
        except requests.exceptions.RequestException:
            pass


@pytest.fixture
def test_user(base_url, auth_headers, session_with_retries):
    """Crea un usuario de prueba y lo elimina al finalizar."""
    user_data = {
        "email": f"test.{random.randint(1000,9999)}@demo.com",
        "password": "Test12345",
        "full_name": "Test User",
        "role": "passenger"
    }

    r = session_with_retries.post(
        f"{base_url}/users/",
        json=user_data,
        headers=auth_headers,
        timeout=REQUEST_TIMEOUT
    )

    if r.status_code == 400:
        pytest.skip(f"No se pudo crear usuario de prueba: {r.text}")

    r.raise_for_status()
    user_response = r.json()

    yield user_response

    try:
        session_with_retries.delete(
            f"{base_url}/users/{user_response['id']}",
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT
        )
    except requests.exceptions.RequestException:
        pass


@pytest.fixture
def api_client():
    """Fixture que proporciona una instancia del cliente API unificado."""
    return APIClient(base_url=BASE_URL)


@pytest.fixture
def authenticated_api_client(api_client, admin_token):
    """Fixture que proporciona una instancia del cliente API con autenticación."""
    api_client.token = admin_token
    return api_client


# Fixtures para los esquemas de validación
@pytest.fixture
def login_schema():
    """Fixture que proporciona el esquema de validación para login."""
    return LOGIN_SCHEMA


@pytest.fixture
def error_schema():
    """Fixture que proporciona el esquema de validación para errores."""
    return ERROR_SCHEMA


@pytest.fixture
def success_schema():
    """Fixture que proporciona el esquema de validación para respuestas exitosas."""
    return SUCCESS_SCHEMA


# Configuración de variables de entorno para tests
def pytest_configure(config):
    """Configuración inicial de pytest."""
    # Establecer variables de entorno por defecto para tests
    os.environ.setdefault("BASE_URL", "https://cf-automation-airline-api.onrender.com")
    os.environ.setdefault("API_RETRIES", "3")
    os.environ.setdefault("API_TIMEOUT", "5")