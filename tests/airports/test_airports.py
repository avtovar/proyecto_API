# -----------------------------------------------------------
# Archivo: test_airports.py
# Descripción:
#   Conjunto de pruebas automatizadas con pytest para la API
#   de aeropuertos. Incluye creación con reintentos, consulta,
#   actualización y eliminación de aeropuertos.
# -----------------------------------------------------------

import pytest
from jsonschema import validate
from tests.airports.test_schema_airports import airport_schema  # Esquema esperado de un aeropuerto
import random
import string
from requests.exceptions import RetryError


# -----------------------------------------------------------
# Función auxiliar: generar código IATA único
# -----------------------------------------------------------
def unique_iata():
    """Genera un código IATA válido y único (3 letras mayúsculas)."""
    return ''.join(random.choices(string.ascii_uppercase, k=3))


# -----------------------------------------------------------
# Función auxiliar: creación de aeropuerto con reintentos
# -----------------------------------------------------------
def create_airport_with_retry(base_url, auth_headers, session_with_retries, max_attempts=3):
    """
    Intenta crear un aeropuerto con reintentos para evitar
    fallos por códigos IATA ya existentes.

    Parámetros:
      - base_url: URL base de la API
      - auth_headers: headers de autenticación
      - session_with_retries: sesión HTTP con reintentos
      - max_attempts: número máximo de intentos (default=3)

    Retorna:
      - JSON del aeropuerto creado si es exitoso
    """
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

        # Caso exitoso
        if response.status_code in [201, 200]:
            return response.json()
        # Caso de código IATA ya existente -> reintentar
        elif response.status_code == 400 and 'exists' in response.text:
            continue
        # Cualquier otro error inesperado
        else:
            pytest.fail(f"Error inesperado al crear aeropuerto: {response.text}")

    # Si después de los intentos no se pudo crear, fallar la prueba
    pytest.fail("No se pudo crear un aeropuerto después de 3 intentos")


# -----------------------------------------------------------
# TEST: Obtener aeropuerto por código
# -----------------------------------------------------------
def test_get_airport_by_code(base_url, auth_headers, session_with_retries):
    """Valida la consulta de un aeropuerto específico por su código IATA."""
    # Crear aeropuerto con reintentos
    airport = create_airport_with_retry(base_url, auth_headers, session_with_retries)
    code = airport["iata_code"]

    # Consultar aeropuerto recién creado
    response = session_with_retries.get(
        f"{base_url}/airports/{code}",
        headers=auth_headers,
        timeout=10
    )

    assert response.status_code == 200
    airport_data = response.json()
    assert airport_data["iata_code"] == code
    # Validar estructura con schema JSON
    validate(instance=airport_data, schema=airport_schema)


# -----------------------------------------------------------
# TEST: Actualizar aeropuerto existente
# -----------------------------------------------------------
def test_update_airport(base_url, auth_headers, session_with_retries):
    """Valida la actualización de datos de un aeropuerto existente."""
    airport = create_airport_with_retry(base_url, auth_headers, session_with_retries)
    code = airport["iata_code"]

    # Datos actualizados
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


# -----------------------------------------------------------
# TEST: Eliminar aeropuerto existente
# -----------------------------------------------------------
def test_delete_airport(base_url, auth_headers, session_with_retries):
    """Valida la eliminación de un aeropuerto existente."""
    airport = create_airport_with_retry(base_url, auth_headers, session_with_retries)
    code = airport["iata_code"]

    # Eliminar aeropuerto
    response = session_with_retries.delete(
        f"{base_url}/airports/{code}",
        headers=auth_headers,
        timeout=10
    )
    assert response.status_code in [200, 204]

    # Verificar que ya no exista
    get_resp = session_with_retries.get(
        f"{base_url}/airports/{code}",
        headers=auth_headers,
        timeout=10
    )
    assert get_resp.status_code == 404
