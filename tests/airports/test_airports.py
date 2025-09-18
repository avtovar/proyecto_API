import pytest
from jsonschema import validate
from test_schema_airports import airport_schema
import uuid


def unique_iata():
    """Genera un código IATA único de 3 letras."""
    return str(uuid.uuid4())[:3].upper()


def test_create_airport_success(base_url, auth_headers, session_with_retries):
    """Crear un nuevo aeropuerto exitosamente"""
    data = {
        "iata_code": unique_iata(),
        "city": "New York",
        "country": "USA"
    }

    response = session_with_retries.post(
        f"{base_url}/airports",
        json=data,
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code in [201, 200], f"Expected 201/200, got {response.status_code}"
    airport = response.json()
    assert "iata_code" in airport
    validate(instance=airport, schema=airport_schema)


def test_create_airport_invalid_data(base_url, auth_headers, session_with_retries):
    """Intentar crear aeropuerto con datos inválidos"""
    data = {
        "iata_code": "ABCD",  # demasiado largo
        "city": "",
        "country": "USA"
    }

    response = session_with_retries.post(
        f"{base_url}/airports",
        json=data,
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
    error = response.json()
    assert "error" in error or "message" in error or "detail" in error


def test_get_all_airports(base_url, auth_headers, session_with_retries):
    """Obtener todos los aeropuertos"""
    response = session_with_retries.get(
        f"{base_url}/airports",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    airports = response.json()
    assert isinstance(airports, list)
    if airports:
        airport = airports[0]
        assert "iata_code" in airport
        assert "city" in airport
        assert "country" in airport


def test_get_airport_by_code(base_url, auth_headers, session_with_retries):
    """Obtener un aeropuerto específico por código"""
    code = unique_iata()
    data = {"iata_code": code, "city": "Test City", "country": "Mexico"}
    create_resp = session_with_retries.post(
        f"{base_url}/airports",
        json=data,
        headers=auth_headers,
        timeout=10
    )
    airport = create_resp.json()
    assert "iata_code" in airport, f"Respuesta inválida: {airport}"

    response = session_with_retries.get(
        f"{base_url}/airports/{code}",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 200
    airport_data = response.json()
    assert airport_data["iata_code"] == code
    validate(instance=airport_data, schema=airport_schema)


def test_get_airport_not_found(base_url, auth_headers, session_with_retries):
    """Intentar obtener aeropuerto inexistente"""
    response = session_with_retries.get(
        f"{base_url}/airports/XXX",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 404


def test_update_airport(base_url, auth_headers, session_with_retries):
    """Actualizar un aeropuerto existente"""
    code = unique_iata()
    data = {"iata_code": code, "city": "Old City", "country": "USA"}
    create_resp = session_with_retries.post(
        f"{base_url}/airports",
        json=data,
        headers=auth_headers,
        timeout=10
    )
    airport = create_resp.json()
    assert "iata_code" in airport, f"Respuesta inválida: {airport}"

    update_data = {"city": "Updated City"}
    response = session_with_retries.put(
        f"{base_url}/airports/{code}",
        json=update_data,
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code in [200, 201]
    updated_airport = response.json()
    assert updated_airport["city"] == "Updated City"


def test_delete_airport(base_url, auth_headers, session_with_retries):
    """Eliminar un aeropuerto"""
    code = unique_iata()
    data = {"iata_code": code, "city": "Temp City", "country": "Spain"}
    create_resp = session_with_retries.post(
        f"{base_url}/airports",
        json=data,
        headers=auth_headers,
        timeout=10
    )
    airport = create_resp.json()
    assert "iata_code" in airport, f"Respuesta inválida: {airport}"

    response = session_with_retries.delete(
        f"{base_url}/airports/{code}",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code in [200, 204]

    get_resp = session_with_retries.get(
        f"{base_url}/airports/{code}",
        headers=auth_headers,
        timeout=10
    )
    assert get_resp.status_code == 404


