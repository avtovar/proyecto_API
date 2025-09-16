import pytest
from jsonschema import validate

# Esquema esperado para aeropuerto
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


def test_get_all_airports(base_url, auth_headers, session_with_retries):
    """Obtiene y valida la lista de aeropuertos."""
    response = session_with_retries.get(
        f"{base_url}/airports/",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    airports = response.json()
    assert isinstance(airports, list), "Response should be a list"

    if airports:  # Si hay aeropuertos, validar el primero
        airport = airports[0]
        assert "iata_code" in airport, "Airport should have iata_code"
        assert "city" in airport, "Airport should have city"
        assert "country" in airport, "Airport should have country"


def test_get_airport_by_code(base_url, auth_headers, session_with_retries, airport):
    """Obtiene un aeropuerto específico por su código IATA y valida su esquema."""
    iata_code = airport["iata_code"]

    response = session_with_retries.get(
        f"{base_url}/airports/{iata_code}",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    airport_data = response.json()
    assert airport_data["iata_code"] == iata_code, "El código IATA no coincide"
    validate(instance=airport_data, schema=airport_schema)
