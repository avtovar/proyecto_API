import pytest
from jsonschema import validate
from test_schema_airports import airport_schema
import random
import string


def unique_iata():
    """Genera un código IATA válido y único (3 letras mayúsculas)."""
    return ''.join(random.choices(string.ascii_uppercase, k=3))


def test_create_airport_success(base_url, auth_headers, session_with_retries):
    """Crear un nuevo aeropuerto exitosamente"""
    max_attempts = 3
    for attempt in range(max_attempts):
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

        if response.status_code in [201, 200]:
            airport = response.json()
            assert "iata_code" in airport, f"Respuesta inválida: {airport}"
            validate(instance=airport, schema=airport_schema)
            return
        else:
            error_data = response.json()
            if 'detail' in error_data and 'exists' in error_data['detail']:
                continue
            else:
                pytest.fail(f"Error inesperado al crear aeropuerto: {response.text}")
    else:
        pytest.fail("No se pudo crear un aeropuerto con código IATA único después de 3 intentos")



def test_create_airport_invalid_data(base_url, auth_headers, session_with_retries):
    """Intentar crear aeropuerto con datos inválidos"""
    data = {
        "iata_code": "123",  # inválido (no cumple regex ^[A-Z]{3}$)
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


def test_update_airport(base_url, auth_headers, session_with_retries):
    """Actualizar un aeropuerto existente"""
    max_attempts = 3
    for attempt in range(max_attempts):
        code = unique_iata()
        data = {"iata_code": code, "city": "Old City", "country": "USA"}
        create_resp = session_with_retries.post(
            f"{base_url}/airports",
            json=data,
            headers=auth_headers,
            timeout=10
        )
        if create_resp.status_code == 201:
            airport = create_resp.json()
            break
        else:
            error_data = create_resp.json()
            if 'detail' in error_data and 'exists' in error_data['detail']:
                continue
            else:
                pytest.fail(f"Error inesperado al crear aeropuerto: {create_resp.text}")
    else:
        pytest.fail("No se pudo crear un aeropuerto con código IATA único después de 3 intentos")

    assert "iata_code" in airport, f"Respuesta inválida: {airport}"

    update_data = {"iata_code": code, "city": "Updated City", "country": "USA"}
    response = session_with_retries.put(
        f"{base_url}/airports/{code}",
        json=update_data,
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
    updated_airport = response.json()
    assert updated_airport["city"] == "Updated City"


def test_delete_airport(base_url, auth_headers, session_with_retries):
    """Eliminar un aeropuerto"""
    max_attempts = 3
    for attempt in range(max_attempts):
        code = unique_iata()
        data = {"iata_code": code, "city": "Temp City", "country": "Spain"}
        create_resp = session_with_retries.post(
            f"{base_url}/airports",
            json=data,
            headers=auth_headers,
            timeout=10
        )
        if create_resp.status_code == 201:
            airport = create_resp.json()
            break
        else:
            error_data = create_resp.json()
            if 'detail' in error_data and 'exists' in error_data['detail']:
                continue
            else:
                pytest.fail(f"Error inesperado al crear aeropuerto: {create_resp.text}")
    else:
        pytest.fail("No se pudo crear un aeropuerto con código IATA único después de 3 intentos")

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