import os
import random
import string
import requests
import pytest
import faker
from dotenv import load_dotenv

load_dotenv()

# URL base de la API
BASE_URL = os.getenv("BASE_URL", "https://cf-automation-airline-api.onrender.com")
AUTH_LOGIN = "/auth/login/"
AIRPORT = "/airports/"
fake = faker.Faker()


@pytest.fixture(scope="session")
def base_url():
    """Fixture que retorna la URL base de la API"""
    return BASE_URL


@pytest.fixture(scope="session")
def admin_token() -> str:
    """Fixture para obtener token de administrador"""
    user = os.getenv("ADMIN_USER", "admin@demo.com")
    pwd = os.getenv("ADMIN_PASS", "admin123")

    r = requests.post(
        BASE_URL + AUTH_LOGIN,
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
        timeout=5
    )

    if r.status_code != 200:
        raise RuntimeError(f"Login failed ({r.status_code}): {r.text}")

    return r.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    """Fixture que retorna headers de autenticación"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def airport(auth_headers):
    """Fixture para crear un aeropuerto temporal para pruebas"""
    airport_data = {
        "iata_code": "".join(random.choices(string.ascii_uppercase, k=3)),
        "city": "La Paz",
        "country": fake.country_code()
    }

    r = requests.post(BASE_URL + AIRPORT, json=airport_data, headers=auth_headers, timeout=5)
    r.raise_for_status()
    airport_response = r.json()

    yield airport_response

    # Cleanup: eliminar el aeropuerto después de la prueba
    try:
        requests.delete(BASE_URL + AIRPORT + f'{airport_response["iata_code"]}', headers=auth_headers, timeout=5)
    except requests.exceptions.RequestException:
        # Si falla el cleanup, continuar de todos modos
        pass