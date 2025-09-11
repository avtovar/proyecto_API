import pytest
import  requests
from jsonschema import validate

BASE_URL = "https://cf-automation-airline-api.onrender.com"
AUTH_LOGIN = "/auth/login/"
AIRPORT = "/airports/"

airport_schema = {
    "type": "object",
    "required": ["iata_code", "city", "country"],
    "properties": {
        "iata_code": {"type": "string", "minLength": 3, "maxLength": 3},
        "city": {"type": "string"},
        "country": {"type": "string"},
    },
    "addtionalProperties": False
}


def test_create_airport_schema(airport):
    validate(instance=airport, schema=airport_schema)


def test_get_all_airports(airport, auth_headers):
    r = requests.get(f"{BASE_URL}{AIRPORT}", headers=auth_headers)
    lista = r.text
    assert r.status_code == 200
    assert r.text != ""



