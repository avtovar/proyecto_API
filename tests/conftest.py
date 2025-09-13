"""
conftest.py
Fixtures globales para pruebas de la API de Aerolínea.

Incluye:
- base_url: URL base de la API.
- admin_token: obtiene token de autenticación de administrador.
- auth_headers: cabeceras con token JWT.
- airport: crea y elimina un aeropuerto temporal.
- user: crea y elimina un usuario temporal.

Requiere variables de entorno en .env:
    ADMIN_USER=usuario_admin
    ADMIN_PASS=clave_admin
    BASE_URL=url_api
"""

import os
import random
import string
import pytest
import requests
import faker
from dotenv import load_dotenv

# 📌 Cargar variables desde archivo .env
load_dotenv()

fake = faker.Faker()


# -------------------- FIXTURES --------------------

@pytest.fixture(scope="session")
def base_url() -> str:
    """Devuelve la URL base de la API"""
    return os.getenv("BASE_URL", "https://cf-automation-airline-api.onrender.com")


@pytest.fixture(scope="session")
def admin_token(base_url: str) -> str:
    """Obtiene un token JWT válido para el administrador"""
    user = os.getenv("ADMIN_USER")
    pwd = os.getenv("ADMIN_PASS")

    if not user or not pwd:
        raise RuntimeError("❌ ADMIN_USER o ADMIN_PASS no están configurados en .env o variables de entorno")

    login_url = f"{base_url}/auth/login/"

    r = requests.post(login_url, data={"username": user, "password": pwd}, timeout=5)
    r.raise_for_status()

    token = r.json().get("access_token")
    if not token:
        raise RuntimeError(f"❌ No se encontró 'access_token' en la respuesta: {r.text}")

    return token


@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    """Devuelve headers con autenticación JWT"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def airport(base_url: str, auth_headers: dict):
    """
    Crea un aeropuerto temporal antes de la prueba
    y lo elimina automáticamente después (teardown).
    """
    airport_data = {
        "iata_code": "".join(random.choices(string.ascii_uppercase, k=3)),
        "city": "La Paz",
        "country": "ARG"
    }

    r = requests.post(f"{base_url}/airports/", json=airport_data, headers=auth_headers, timeout=5)
    r.raise_for_status()
    airport_response = r.json()

    yield airport_response  # Entrega el aeropuerto a la prueba

    # Teardown: borrar aeropuerto creado
    requests.delete(
        f"{base_url}/airports/{airport_response['iata_code']}",
        headers=auth_headers,
        timeout=5
    )


@pytest.fixture
def user(base_url: str, auth_headers: dict, role: str = "passenger"):
    """
    Crea un usuario temporal antes de la prueba
    y lo elimina automáticamente después (teardown).
    """
    user_data = {
        "email": fake.email(),
        "password": fake.password(),
        "full_name": fake.name(),
        "role": role
    }

    r = requests.post(f"{base_url}/users/", json=user_data, headers=auth_headers, timeout=5)
    r.raise_for_status()
    user_created = r.json()

    yield user_created  # Entrega el usuario a la prueba

    # Teardown: borrar usuario creado
    requests.delete(
        f"{base_url}/users/{user_created['id']}",
        headers=auth_headers,
        timeout=5
    )
