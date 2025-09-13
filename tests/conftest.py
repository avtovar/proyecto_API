"""
🔹 Fixtures y pruebas automatizadas para la API de Aerolínea.
Este módulo define utilidades de prueba para autenticación, creación de aeropuertos y usuarios,
usando pytest + requests.

- Se cargan variables de entorno desde `.env` (ADMIN_USER, ADMIN_PASS).
- Se gestionan recursos de prueba (airport, user) con setup y teardown automático.
- Se generan datos aleatorios realistas con Faker.

Requisitos:
    pip install pytest requests python-dotenv faker
"""

import os
import random
import string
import requests
import pytest
import faker
from dotenv import load_dotenv

# 📌 Cargar variables desde archivo .env (si existe)
load_dotenv()

# 🌍 Endpoints base de la API
BASE_URL = "https://cf-automation-airline-api.onrender.com"
AUTH_LOGIN = "/auth/login/"
AIRPORT = "/airports/"
USERS = "/users"

# 🧪 Generador de datos aleatorios
fake = faker.Faker()


# -------------------- FIXTURES --------------------

@pytest.fixture(scope="session")
def admin_token() -> str:
    """
    Obtiene un token de administrador para autenticación.
    Requiere ADMIN_USER y ADMIN_PASS definidos en .env o en variables de entorno.
    """
    user = os.getenv("ADMIN_USER")
    pwd = os.getenv("ADMIN_PASS")

    if not user or not pwd:
        raise RuntimeError("❌ ADMIN_USER o ADMIN_PASS no están configurados")

    r = requests.post(
        BASE_URL + AUTH_LOGIN,
        data={"username": user, "password": pwd},
        timeout=5
    )
    r.raise_for_status()
    return r.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    """ Devuelve headers con el token de administrador. """
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def airport(auth_headers):
    """
    Crea un aeropuerto temporal antes de la prueba.
    Lo elimina automáticamente después (teardown).
    """
    aiport_data = {
        "iata_code": "".join(random.choices(string.ascii_uppercase, k=3)),
        "city": "La Paz",
        "country": fake.country_code()
    }

    r = requests.post(BASE_URL + AIRPORT, json=aiport_data, headers=auth_headers, timeout=5)
    r.raise_for_status()
    airport_response = r.json()

    yield airport_response  # 🔹 Se entrega a la prueba

    # 🔻 Teardown: borrar el aeropuerto creado
    requests.delete(
        BASE_URL + AIRPORT + f'{airport_response["iata_code"]}',
        headers=auth_headers,
        timeout=5
    )


@pytest.fixture
def user(auth_headers, role: str = "passenger"):
    """
    Crea un usuario temporal antes de la prueba.
    Lo elimina automáticamente después (teardown).
    """
    user_data = {
        "email": fake.email(),
        "password": fake.password(),
        "full_name": fake.name(),
        "role": role
    }

    r = requests.post(f"{BASE_URL}{USERS}", json=user_data, headers=auth_headers, timeout=5)
    r.raise_for_status()
    user_created = r.json()

    yield user_created  # 🔹 Se entrega a la prueba

    # 🔻 Teardown: borrar usuario creado
    requests.delete(
        f"{BASE_URL}{USERS}/{user_created['id']}",
        headers=auth_headers,
        timeout=5
    )


# -------------------- TESTS --------------------

def test_admin_token(admin_token):
    """ Verifica que se puede obtener un token válido. """
    assert isinstance(admin_token, str)
    assert len(admin_token) > 10  # Un token JWT suele ser largo


def test_airport(airport):
    """ Verifica que se puede crear un aeropuerto correctamente. """
    assert "iata_code" in airport
    assert "city" in airport
    assert "country" in airport
    print("✅ Aeropuerto creado:", airport)
