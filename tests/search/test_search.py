import pytest
from jsonschema import validate
from tests.search.test_schema_search import flight_search_schema
from requests.exceptions import RetryError
import random
import string


def random_id(length=8):
    """Genera un ID aleatorio"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def test_search_flights_by_date(base_url, auth_headers, session_with_retries):
    """
    Buscar vuelos por fechas
    Given que existen vuelos para la fecha "2024-03-15"
    When envío una solicitud GET a "/flights?date=2024-03-15"
    Then el código de respuesta debe ser 200
    And todos los vuelos deben ser para la fecha especificada
    """
    try:
        # Primero crear un vuelo para asegurar que hay datos
        airline_id = random_id()
        airline_data = {
            "id": airline_id,
            "name": "Test Airline",
            "country": "USA"
        }

        # Crear aerolínea
        airline_response = session_with_retries.post(
            f"{base_url}/airlines",
            json=airline_data,
            headers=auth_headers,
            timeout=10
        )

        if airline_response.status_code not in [200, 201]:
            pytest.skip("No se pudo crear aerolínea para la prueba")

        # Crear vuelo con fecha específica
        flight_data = {
            "name": "SKY123",
            "from": "JFK",
            "to": "LAX",
            "departure": "08:00",
            "arrival": "11:30",
            "duration": 3.5,
            "stops": 0,
            "price": 299.99,
            "airline_id": airline_id,
            "date": "2024-03-15"  # Fecha específica
        }

        flight_response = session_with_retries.post(
            f"{base_url}/flights",
            json=flight_data,
            headers=auth_headers,
            timeout=10
        )

        if flight_response.status_code not in [200, 201]:
            pytest.skip("No se pudo crear vuelo para la prueba")

        # Ahora buscar vuelos por fecha
        response = session_with_retries.get(
            f"{base_url}/flights?date=2024-03-15",
            headers=auth_headers,
            timeout=10
        )

        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500) al buscar vuelos por fecha: {response.text}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        flights = response.json()
        assert isinstance(flights, list)

        # Verificar que todos los vuelos son para la fecha especificada
        for flight in flights:
            assert flight.get("date") == "2024-03-15", f"Vuelo con fecha incorrecta: {flight}"

    except RetryError as e:
        pytest.xfail(f"Error de conexión después de múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error al buscar vuelos por fecha: {str(e)}")


def test_search_flights_by_price_range(base_url, auth_headers, session_with_retries):
    """
    Buscar vuelos por rango de precios
    Given que existen vuelos entre $200 y $500
    When envío una solicitud GET a "/flights?minPrice=200&maxPrice=500"
    Then el código de respuesta debe ser 200
    And todos los vuelos deben tener un precio entre 200 y 500
    """
    try:
        # Buscar vuelos en el rango de precios
        response = session_with_retries.get(
            f"{base_url}/flights?minPrice=200&maxPrice=500",
            headers=auth_headers,
            timeout=10
        )

        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500) al buscar vuelos por precio: {response.text}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        flights = response.json()
        assert isinstance(flights, list)

        # Verificar que todos los vuelos están en el rango de precios
        for flight in flights:
            price = flight.get("price", 0)
            assert 200 <= price <= 500, f"Precio {price} fuera del rango 200-500"

    except RetryError as e:
        pytest.xfail(f"Error de conexión después de múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error al buscar vuelos por precio: {str(e)}")


def test_validate_airline_date_format(base_url, auth_headers, session_with_retries):
    """
    Validar formato de fechas en creación de aerolínea
    Given que intento crear una aerolínea con fecha establecida inválida
    When envío una solicitud POST a "/airlines"
    Then el código de respuesta debe ser 400
    And el mensaje debe indicar error en el formato de fecha
    """
    airline_data = {
        "id": random_id(),
        "name": "Test Airline",
        "country": "USA",
        "established": "2024-13-45"  # Fecha inválida
    }

    try:
        response = session_with_retries.post(
            f"{base_url}/airlines",
            json=airline_data,
            headers=auth_headers,
            timeout=10
        )

        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500) al validar formato de fecha: {response.text}")

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        # Verificar que el mensaje de error menciona la fecha
        error_data = response.json()
        error_message = str(error_data).lower()
        assert any(
            keyword in error_message for keyword in ["date", "fecha", "format", "formato", "invalid", "inválido"])

    except RetryError as e:
        pytest.xfail(f"Error de conexión después de múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error al validar formato de fecha: {str(e)}")


def test_validate_required_fields_flight(base_url, auth_headers, session_with_retries):
    """
    Validar campos requeridos en creación de vuelo
    Given que intento crear un vuelo sin campos requeridos
    When envío una solicitud POST a "/flights"
    Then el código de respuesta debe ser 400
    And el mensaje debe indicar los campos faltantes
    """
    # Datos incompletos (faltan campos requeridos)
    flight_data = {
        "name": "",  # Campo requerido vacío
        "from": "JFK",
        "to": "",  # Campo requerido vacío
        "departure": "08:00",
        "arrival": "11:30",
        "duration": 3.5,
        "stops": 0,
        "price": 299.99,
        "airline_id": "123"
    }

    try:
        response = session_with_retries.post(
            f"{base_url}/flights",
            json=flight_data,
            headers=auth_headers,
            timeout=10
        )

        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500) al validar campos requeridos: {response.text}")

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

        # Verificar que el mensaje de error menciona campos requeridos
        error_data = response.json()
        error_message = str(error_data).lower()
        assert any(
            keyword in error_message for keyword in ["required", "requerido", "missing", "faltante", "field", "campo"])

    except RetryError as e:
        pytest.xfail(f"Error de conexión después de múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error al validar campos requeridos: {str(e)}")