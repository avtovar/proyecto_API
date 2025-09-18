import pytest
from jsonschema import validate
from test_schema_airports import airport_schema, airline_schema


# ======================
# TESTS PARA AEROPUERTOS
# ======================

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


# =====================
# TESTS PARA AEROLÍNEAS
# =====================

def test_create_airline_success(base_url, auth_headers, session_with_retries):
    """Crear una nueva aerolínea exitosamente"""
    data = {
        "name": "Sky Airlines",
        "country": "USA",
        "logo": "sky-logo.png",
        "slogan": "Fly with us",
        "head_quaters": "New York",
        "website": "sky.com",
        "established": "1990-01-01"
    }

    response = session_with_retries.post(
        f"{base_url}/airlines",
        json=data,
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    airline = response.json()
    assert "id" in airline
    assert airline["name"] == "Sky Airlines"
    validate(instance=airline, schema=airline_schema)


def test_create_airline_invalid_data(base_url, auth_headers, session_with_retries):
    """Intentar crear aerolínea con datos inválidos"""
    data = {
        "name": "",
        "country": "USA",
        "established": "fecha-invalida"
    }

    response = session_with_retries.post(
        f"{base_url}/airlines",
        json=data,
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    error = response.json()
    assert "error" in error or "message" in error


def test_get_all_airlines(base_url, auth_headers, session_with_retries):
    """Obtener todas las aerolíneas"""
    response = session_with_retries.get(
        f"{base_url}/airlines",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    airlines = response.json()
    assert isinstance(airlines, list)
    if airlines:
        airline = airlines[0]
        assert "id" in airline
        assert "name" in airline
        assert "country" in airline


def test_get_airline_by_id(base_url, auth_headers, session_with_retries):
    """Obtener una aerolínea específica por ID"""
    # Crear primero para garantizar que exista
    data = {
        "name": "Test Airline",
        "country": "Mexico",
        "established": "2000-01-01"
    }
    create_resp = session_with_retries.post(
        f"{base_url}/airlines",
        json=data,
        headers=auth_headers,
        timeout=10
    )
    airline_id = create_resp.json()["id"]

    response = session_with_retries.get(
        f"{base_url}/airlines/{airline_id}",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 200
    airline = response.json()
    assert airline["id"] == airline_id
    validate(instance=airline, schema=airline_schema)


def test_get_airline_not_found(base_url, auth_headers, session_with_retries):
    """Intentar obtener aerolínea inexistente"""
    response = session_with_retries.get(
        f"{base_url}/airlines/999",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 404


def test_update_airline(base_url, auth_headers, session_with_retries):
    """Actualizar una aerolínea existente"""
    # Crear primero
    data = {
        "name": "Sky Air",
        "country": "USA",
        "established": "1990-01-01"
    }
    create_resp = session_with_retries.post(
        f"{base_url}/airlines",
        json=data,
        headers=auth_headers,
        timeout=10
    )
    airline_id = create_resp.json()["id"]

    # Actualizar
    update_data = {"name": "Sky Air 2.0", "slogan": "Better flights"}
    response = session_with_retries.put(
        f"{base_url}/airlines/{airline_id}",
        json=update_data,
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 200
    updated_airline = response.json()
    assert updated_airline["name"] == "Sky Air 2.0"
    assert updated_airline["slogan"] == "Better flights"


def test_delete_airline(base_url, auth_headers, session_with_retries):
    """Eliminar una aerolínea"""
    # Crear primero
    data = {
        "name": "Temp Airline",
        "country": "Spain",
        "established": "2010-05-05"
    }
    create_resp = session_with_retries.post(
        f"{base_url}/airlines",
        json=data,
        headers=auth_headers,
        timeout=10
    )
    airline_id = create_resp.json()["id"]

    # Eliminar
    response = session_with_retries.delete(
        f"{base_url}/airlines/{airline_id}",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 200

    # Verificar que ya no existe
    get_resp = session_with_retries.get(
        f"{base_url}/airlines/{airline_id}",
        headers=auth_headers,
        timeout=10
    )
    assert get_resp.status_code == 404
