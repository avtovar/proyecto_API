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

        yield airport_response  # Se entrega al test

    finally:
        # Cleanup: eliminar el aeropuerto después de la prueba
        try:
            session_with_retries.delete(
                BASE_URL + AIRPORT + f'{airport_data["iata_code"]}',
                headers=auth_headers,
                timeout=REQUEST_TIMEOUT
            )
        except requests.exceptions.RequestException:
            pass  # si falla el cleanup, continuar


@pytest.fixture
def test_user(base_url, auth_headers, session_with_retries):
    """Crea un usuario de prueba y lo elimina al finalizar."""
    user_data = {
        "email": "test.user@example.com",
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
    r.raise_for_status()
    user_response = r.json()

    yield user_response

    # Cleanup: eliminar usuario después de la prueba
    try:
        session_with_retries.delete(
            f"{base_url}/users/{user_response['id']}",
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT
        )
    except requests.exceptions.RequestException:
        pass















import requests
import pytest
from jsonschema import validate

# Esquema esperado para un usuario
user_schema = {
    "type": "object",
    "required": ["id", "email", "full_name", "role"],
    "properties": {
        "id": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "full_name": {"type": "string"},
        "role": {"type": "string", "enum": ["passenger", "admin"]}
    },
    "additionalProperties": False
}


@pytest.fixture
def test_user(base_url, auth_headers):
    """Fixture para crear un usuario de prueba"""
    user_data = {
        "email": "alondra.tovar@airline.com",
        "password": "Alon12345",
        "full_name": "Alondra Tovar",
        "role": "admin"
    }

    response = requests.post(
        f"{base_url}/users/",
        json=user_data,
        headers=auth_headers
    )
    response.raise_for_status()

    yield response.json()

    # Cleanup: eliminar usuario después de la prueba
    user_id = response.json()["id"]
    requests.delete(f"{base_url}/users/{user_id}", headers=auth_headers)


def test_create_user_schema(test_user):
    """Valida que el usuario creado cumpla con el esquema JSON esperado."""
    validate(instance=test_user, schema=user_schema)


def test_get_all_users(base_url, auth_headers):
    """
    Obtiene todos los usuarios de la API en bloques (paginación).
    Verifica que devuelve una lista de usuarios con id y email válidos.
    """
    limit = 10
    skip = 0
    results = []

    while True:
        r = requests.get(
            f"{base_url}/users/",
            headers=auth_headers,
            params={"skip": skip, "limit": limit},
            timeout=5
        )
        r.raise_for_status()
        users_list = r.json()

        if not users_list:
            break

        results.extend(users_list)
        skip += limit

    # Validaciones
    assert isinstance(results, list)
    if results:
        assert "id" in results[0]
        assert "email" in results[0]


def test_delete_user_alondra(base_url, auth_headers):
    """
    Busca y elimina al usuario cuyo full_name sea 'Alondra Tovar'.
    """
    # Buscar usuarios
    r = requests.get(f"{base_url}/users/", headers=auth_headers)
    r.raise_for_status()
    users = r.json()

    # Buscar el usuario con nombre "Alondra Tovar"
    alondra = next((u for u in users if u.get("full_name") == "Alondra Tovar"), None)

    assert alondra is not None, "No se encontró un usuario con full_name='Alondra Tovar'"

    user_id = alondra["id"]
    delete_response = requests.delete(f"{base_url}/users/{user_id}", headers=auth_headers)

    # Validar que se eliminó correctamente
    assert delete_response.status_code in [200, 204], f"Error al eliminar usuario: {delete_response.text}"


