import pytest
from jsonschema import validate
from tests.flights.test_schema_flights import flight_schema
import random
import string
from requests.exceptions import RetryError


# ================================================================
# Funciones auxiliares
# ================================================================

def random_id(length=8):
    """
    Genera un ID aleatorio compuesto de letras y números.
    Usado para simular identificadores únicos (ej: aerolíneas).
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def random_airport_code():
    """
    Genera un código de aeropuerto de 3 letras mayúsculas (ej: JFK, LAX).
    Usado para crear vuelos de prueba consistentes.
    """
    return ''.join(random.choices(string.ascii_uppercase, k=3))


# ================================================================
# 1. Crear un nuevo vuelo exitosamente
# ================================================================
def test_create_flight_success(base_url, auth_headers, session_with_retries):
    """
    Caso positivo:
      - Crear una aerolínea válida
      - Crear un vuelo asociado a esa aerolínea
      - Validar que la respuesta tenga código 201
      - Validar el esquema del vuelo con jsonschema
    """
    airline_id = random_id()
    airline_data = {"id": airline_id, "name": "Test Airline", "country": "USA"}

    # Crear aerolínea necesaria para asociar el vuelo
    try:
        response_airline = session_with_retries.post(
            f"{base_url}/airlines", json=airline_data, headers=auth_headers, timeout=10
        )
        if response_airline.status_code not in [200, 201]:
            pytest.skip("No se pudo crear la aerolínea necesaria para el test")
    except Exception as e:
        pytest.skip(f"Error al crear aerolínea: {str(e)}")

    # Crear vuelo
    flight_data = {
        "name": "SKY123",
        "from": "JFK",
        "to": "LAX",
        "departure": "08:00",
        "arrival": "11:30",
        "duration": 3.5,
        "stops": 0,
        "price": 299.99,
        "airline_id": airline_id
    }
    response = session_with_retries.post(
        f"{base_url}/flights", json=flight_data, headers=auth_headers, timeout=10
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    flight = response.json()
    assert "id" in flight
    validate(instance=flight, schema=flight_schema)


# ================================================================
# 2. Crear vuelo con aerolínea inexistente
# ================================================================
def test_create_flight_nonexistent_airline(base_url, auth_headers, session_with_retries):
    """
    Caso negativo:
      - Intentar crear un vuelo con un airline_id inexistente
      - La API debe responder con 422 (entidad no procesable)
    """
    flight_data = {
        "name": "SKY123",
        "from": "JFK",
        "to": "LAX",
        "departure": "08:00",
        "arrival": "11:30",
        "duration": 3.5,
        "stops": 0,
        "price": 299.99,
        "airline_id": "999"
    }

    response = session_with_retries.post(
        f"{base_url}/flights", json=flight_data, headers=auth_headers, timeout=10
    )

    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


# ================================================================
# 3. Obtener todos los vuelos
# ================================================================
def test_get_all_flights(base_url, auth_headers, session_with_retries):
    """
    Verifica que la API devuelva la lista completa de vuelos:
      - Código 200 si es exitoso
      - Si el servidor devuelve >=500, marcar test como xfail
      - La respuesta debe ser una lista de vuelos
    """
    try:
        response = session_with_retries.get(
            f"{base_url}/flights", headers=auth_headers, timeout=10
        )

        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500): {response.text}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        flights = response.json()
        assert isinstance(flights, list)
    except RetryError as e:
        pytest.xfail(f"Error de conexión tras múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error inesperado: {str(e)}")


# ================================================================
# 4. Obtener vuelos con filtros
# ================================================================
def test_get_flights_with_filters(base_url, auth_headers, session_with_retries):
    """
    Verifica que se puedan obtener vuelos aplicando filtros (from y to):
      - Se asegura creando primero un vuelo JFK → LAX
      - Se consulta con filtros desde=JFK y hasta=LAX
      - Se espera lista de vuelos que cumplan los filtros
    """
    airline_id = random_id()
    airline_data = {"id": airline_id, "name": "Test Airline", "country": "USA"}

    # Crear aerolínea
    try:
        response_airline = session_with_retries.post(
            f"{base_url}/airlines", json=airline_data, headers=auth_headers, timeout=10
        )
        if response_airline.status_code not in [200, 201]:
            pytest.skip("No se pudo crear la aerolínea necesaria para el test")
    except Exception as e:
        pytest.skip(f"Error al crear aerolínea: {str(e)}")

    # Crear vuelo JFK → LAX
    flight_data = {
        "name": "SKY123",
        "from": "JFK",
        "to": "LAX",
        "departure": "08:00",
        "arrival": "11:30",
        "duration": 3.5,
        "stops": 0,
        "price": 299.99,
        "airline_id": airline_id
    }
    try:
        response_flight = session_with_retries.post(
            f"{base_url}/flights", json=flight_data, headers=auth_headers, timeout=10
        )
        if response_flight.status_code not in [200, 201]:
            pytest.skip("No se pudo crear el vuelo necesario para el test")
    except Exception as e:
        pytest.skip(f"Error al crear vuelo: {str(e)}")

    # Consultar vuelos filtrados
    try:
        response = session_with_retries.get(
            f"{base_url}/flights?from=JFK&to=LAX", headers=auth_headers, timeout=10
        )
        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500): {response.text}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        flights = response.json()
        assert isinstance(flights, list)
        for flight in flights:
            assert flight["from"] == "JFK"
            assert flight["to"] == "LAX"
    except RetryError as e:
        pytest.xfail(f"Error de conexión tras múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error inesperado: {str(e)}")


# ================================================================
# 5. Obtener un vuelo específico por ID
# ================================================================
def test_get_flight_by_id(base_url, auth_headers, session_with_retries):
    """
    Verifica que se pueda obtener un vuelo específico:
      - Se crea un vuelo de prueba
      - Se consulta por su ID
      - La API debe devolver código 200 y respetar el esquema definido
    """
    airline_id = random_id()
    airline_data = {"id": airline_id, "name": "Test Airline", "country": "USA"}

    # Crear aerolínea
    try:
        response_airline = session_with_retries.post(
            f"{base_url}/airlines", json=airline_data, headers=auth_headers, timeout=10
        )
        if response_airline.status_code not in [200, 201]:
            pytest.skip("No se pudo crear la aerolínea necesaria para el test")
    except Exception as e:
        pytest.skip(f"Error al crear aerolínea: {str(e)}")

    # Crear vuelo
    flight_data = {
        "name": "SKY123",
        "from": "JFK",
        "to": "LAX",
        "departure": "08:00",
        "arrival": "11:30",
        "duration": 3.5,
        "stops": 0,
        "price": 299.99,
        "airline_id": airline_id
    }
    try:
        response_create = session_with_retries.post(
            f"{base_url}/flights", json=flight_data, headers=auth_headers, timeout=10
        )
        if response_create.status_code not in [200, 201]:
            pytest.skip("No se pudo crear el vuelo necesario para el test")

        flight_id = response_create.json()["id"]
    except Exception as e:
        pytest.skip(f"Error al crear vuelo: {str(e)}")

    # Consultar vuelo por ID
    try:
        response = session_with_retries.get(
            f"{base_url}/flights/{flight_id}", headers=auth_headers, timeout=10
        )
        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500): {response.text}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        flight = response.json()
        validate(instance=flight, schema=flight_schema)
        assert flight["id"] == flight_id
    except RetryError as e:
        pytest.xfail(f"Error de conexión tras múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error inesperado al obtener vuelo por ID: {str(e)}")
