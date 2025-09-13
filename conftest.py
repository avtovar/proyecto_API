import os
import random
import string

import requests, pytest, faker
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://cf-automation-airline-api.onrender.com"
AUTH_LOGIN = "/auth/login/"
AIRPORT = "/airports/"
fake = faker.Faker()

@pytest.fixture(scope="session")
def admin_token() -> str:
    user = os.getenv("ADMIN_USER")
    pwd = os.getenv("ADMIN_PASS")

    r = requests.post(BASE_URL + AUTH_LOGIN,
                      data={"username": user, "password": pwd},
                      timeout=5)

    r.raise_for_status()
    return r.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def airport(auth_headers):
    aiport_data = {
      "iata_code": "".join(random.choices(string.ascii_uppercase, k=3)),
      "city": "La Paz",
      "country": fake.country_code()
    }

    r = requests.post(BASE_URL + AIRPORT, json=aiport_data, headers=auth_headers, timeout=5)
    r.raise_for_status()
    airport_response = r.json()
    yield airport_response
    requests.delete(BASE_URL + AIRPORT + f'{airport_response["iata_code"]}', headers=auth_headers, timeout=5)


def test_admin_token(admin_token):
    return admin_token

def test_airport(airport):
    print(airport)