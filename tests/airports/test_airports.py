import pytest
import requests
from jsonschema import validate

# Esquema para aeropuerto
airport_schema = {
    "type": "object",
    "required": ["iata_code", "city", "country"],
    "properties": {
        "iata_code": {"type": "string", "minLength": 3, "maxLength": 3},
        "city": {"type": "string"},
        "country": {"type": "string"},
    },
    "additionalProperties": False
}


def test_create_airport_schema(airport):
    """Valida que el aeropuerto creado cumpla con el esquema JSON esperado."""
    validate(instance=airport, schema=airport_schema)


def test_get_all_airports(base_url, auth_headers):
    """Obtiene y valida la lista de aeropuertos"""
    response = requests.get(f"{base_url}/airports/", headers=auth_headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    airports = response.json()
    assert isinstance(airports, list), "Response should be a list"

    if airports:  # Si hay aeropuertos, validar el primero
        assert "iata_code" in airports[0], "Airport should have iata_code"
        assert "city" in airports[0], "Airport should have city"
        assert "country" in airports[0], "Airport should have country"


def test_get_airport_by_code(base_url, auth_headers, airport):
    """Obtiene un aeropuerto específico por su código IATA"""
    iata_code = airport["iata_code"]
    response = requests.get(f"{base_url}/airports/{iata_code}", headers=auth_headers)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    airport_data = response.json()
    assert airport_data["iata_code"] == iata_code
    validate(instance=airport_data, schema=airport_schema)