import pytest
from jsonschema import validate
from tests.airports.test_schema_airports import airport_schema
import random
import string
from requests.exceptions import RetryError


def unique_iata():
    """Genera un código IATA válido y único (3 letras mayúsculas)."""
    return ''.join(random.choices(string.ascii_uppercase, k=3))


def create_airport_with_retry(base_url, auth_headers, session_with_retries, max_attempts=3):
    """Intenta crear un aeropuerto con reintentos para evitar conflictos de códigos existentes."""
    for attempt in range(max_attempts):
        data = {
            "iata_code": unique_iata(),
            "city": "Test City",
            "country": "Test Country"
        }

        response = session_with_retries.post(
            f"{base_url}/airports",
            json=data,
            headers=auth_headers,
            timeout=10
        )

        if response.status_code in [201, 200]:
            return response.json()
        elif response.status_code == 400 and 'exists' in response.text:
            continue  # Intentar con otro código
        else:
            pytest.fail(f"Error inesperado al crear aeropuerto: {response.text}")

    pytest.fail("No se pudo crear un aeropuerto después de 3 intentos")


def test_get_airport_by_code(base_url, auth_headers, session_with_retries):
    """Obtener un aeropuerto específico por código"""
    # Crear aeropuerto con manejo de reintentos
    airport = create_airport_with_retry(base_url, auth_headers, session_with_retries)
    code = airport["iata_code"]

    # Ahora obtener el aeropuerto
    response = session_with_retries.get(
        f"{base_url}/airports/{code}",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 200
    airport_data = response.json()
    assert airport_data["iata_code"] == code
    validate(instance=airport_data, schema=airport_schema)


# Aplicar el mismo patrón a las otras funciones de prueba que crean aeropuertos
def test_update_airport(base_url, auth_headers, session_with_retries):
    """Actualizar un aeropuerto existente"""
    airport = create_airport_with_retry(base_url, auth_headers, session_with_retries)
    code = airport["iata_code"]

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
    airport = create_airport_with_retry(base_url, auth_headers, session_with_retries)
    code = airport["iata_code"]

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