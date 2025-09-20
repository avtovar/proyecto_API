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

# ======================================================
# Configuración de imports y path
# ======================================================

# Añadir el directorio raíz del proyecto al path de Python
# Esto permite importar el módulo api_client sin errores.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar cliente API y esquemas de validación
from api_client import APIClient, LOGIN_SCHEMA, ERROR_SCHEMA, SUCCESS_SCHEMA

# Cargar variables de entorno desde archivo .env
load_dotenv()

# ======================================================
# Configuración base de la API
# ======================================================

BASE_URL = os.getenv("BASE_URL", "https://cf-automation-airline-api.onrender.com")
AUTH_LOGIN = "/auth/login/"
AIRPORT = "/airports/"
fake = faker.Faker()

# Configuración de timeouts y reintentos
REQUEST_TIMEOUT = 15       # Tiempo máximo por request
MAX_RETRIES = 3            # Número máximo de reintentos
BACKOFF_FACTOR = 0.5       # Espera exponencial entre intentos

# ======================================================
# FIXTURES DE SESIÓN Y CONFIGURACIÓN
# ======================================================

@pytest.fixture(scope="session")
def session_with_retries():
    """
    Crea una sesión HTTP persistente con soporte para reintentos automáticos.

    - Reintenta en errores como 429, 500, 502, 503, 504.
    - Usa un backoff exponencial para evitar saturar el servidor.
    """
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
    """Devuelve la URL base de la API."""
    return BASE_URL


@pytest.fixture(scope="session")
def admin_token(session_with_retries) -> str:
    """
    Realiza login como administrador y devuelve un token válido.

    - Usa credenciales desde variables de entorno ADMIN_USER y ADMIN_PASS.
    - Si falla, corta la ejecución de pytest.
    """
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
    """Devuelve headers de autenticación con Bearer token."""
    return {"Authorization": f"Bearer {admin_token}"}

# ======================================================
# FIXTURES DE RECURSOS TEMPORALES
# ======================================================

@pytest.fixture
def airport(auth_headers, session_with_retries):
    """
    Crea un aeropuerto temporal para pruebas y lo elimina al finalizar.

    - Usa un código IATA aleatorio.
    - Si no se puede crear, el test se salta.
    """
    airport_data = {
        "iata_code": "".join(random.choices(string.ascii_uppercase, k=3)),
        "city": "La Paz",
        "country": fake.country()  # País aleatorio
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
        # Cleanup: eliminar aeropuerto al finalizar test
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
    """
    Crea un usuario de prueba temporal y lo elimina al finalizar.

    - Genera un email aleatorio.
    - Si no se puede crear, se salta el test.
    """
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

    yield user_response  # Se entrega al test

    # Cleanup: eliminar usuario
    try:
        session_with_retries.delete(
            f"{base_url}/users/{user_response['id']}",
            headers=auth_headers,
            timeout=REQUEST_TIMEOUT
        )
    except requests.exceptions.RequestException:
        pass

# ======================================================
# FIXTURES DE CLIENTE API
# ======================================================

@pytest.fixture
def api_client():
    """Devuelve una instancia del cliente API sin autenticación."""
    return APIClient(base_url=BASE_URL)


@pytest.fixture
def authenticated_api_client(api_client, admin_token):
    """Devuelve cliente API ya autenticado con token de administrador."""
    api_client.token = admin_token
    return api_client

# ======================================================
# FIXTURES DE ESQUEMAS
# ======================================================

@pytest.fixture
def login_schema():
    """Proporciona el esquema de validación para login."""
    return LOGIN_SCHEMA


@pytest.fixture
def error_schema():
    """Proporciona el esquema de validación para errores."""
    return ERROR_SCHEMA


@pytest.fixture
def success_schema():
    """Proporciona el esquema de validación para respuestas exitosas."""
    return SUCCESS_SCHEMA

# ======================================================
# CONFIGURACIÓN GLOBAL DE PYTEST
# ======================================================

def pytest_configure(config):
    """
    Configuración inicial de pytest.

    - Define valores por defecto de variables de entorno
      si no están definidas.
    """
    os.environ.setdefault("BASE_URL", "https://cf-automation-airline-api.onrender.com")
    os.environ.setdefault("API_RETRIES", "3")
    os.environ.setdefault("API_TIMEOUT", "5")
