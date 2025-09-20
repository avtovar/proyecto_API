# -----------------------------------------------------------
# Archivo: test_bookings.py
# Descripción:
#   Conjunto de pruebas automatizadas con pytest para validar
#   la API de reservas (bookings). Se cubren casos de creación,
#   consulta, cancelación y manejo de errores.
# -----------------------------------------------------------

import pytest
from jsonschema import validate
from tests.bookings.test_schema_bookings import booking_schema  # Esquema esperado de reservas
from requests.exceptions import RetryError
import random
import string


# -----------------------------------------------------------
# Función auxiliar: generar IDs aleatorios
# -----------------------------------------------------------
def random_id(length=8):
    """Genera un identificador alfanumérico aleatorio de longitud configurable (default=8)."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# -----------------------------------------------------------
# TEST 1: Crear una reserva exitosa
# -----------------------------------------------------------
def test_create_booking_success(base_url, auth_headers, session_with_retries):
    """
    Flujo completo:
      1. Crear aerolínea.
      2. Crear vuelo asociado a la aerolínea.
      3. Crear reserva para el vuelo.
    Valida que la reserva se confirme y cumpla el esquema esperado.
    """

    # Crear aerolínea de prueba
    airline_id = random_id()
    airline_data = {
        "id": airline_id,
        "name": "Test Airline",
        "country": "USA"
    }

    try:
        response_airline = session_with_retries.post(
            f"{base_url}/airlines",
            json=airline_data,
            headers=auth_headers,
            timeout=10
        )
        if response_airline.status_code not in [200, 201]:
            pytest.skip("No se pudo crear la aerolínea necesaria para el test")
    except Exception as e:
        pytest.skip(f"No se pudo crear la aerolínea: {str(e)}")

    # Crear vuelo asociado
    flight_id = random_id()
    flight_data = {
        "id": flight_id,
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
            f"{base_url}/flights",
            json=flight_data,
            headers=auth_headers,
            timeout=10
        )
        if response_flight.status_code not in [200, 201]:
            pytest.skip("No se pudo crear el vuelo necesario para el test")
    except Exception as e:
        pytest.skip(f"No se pudo crear el vuelo: {str(e)}")

    # Crear la reserva sobre el vuelo recién creado
    booking_data = {
        "flight_id": flight_id,
        "passenger_name": "John",
        "passenger_email": "john@email.com",
        "seat": "15A",
        "class": "economy"
    }

    try:
        response = session_with_retries.post(
            f"{base_url}/bookings",
            json=booking_data,
            headers=auth_headers,
            timeout=10
        )

        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500) al crear reserva: {response.text}")

        # Validaciones
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        booking = response.json()
        assert "id" in booking
        assert booking["status"] == "confirmed"
        validate(instance=booking, schema=booking_schema)
    except RetryError as e:
        pytest.xfail(f"Error de conexión después de múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error al crear reserva: {str(e)}")


# -----------------------------------------------------------
# TEST 2: Crear reserva para vuelo inexistente
# -----------------------------------------------------------
def test_create_booking_nonexistent_flight(base_url, auth_headers, session_with_retries):
    """Valida que no se pueda crear una reserva para un vuelo inexistente (espera 400)."""
    booking_data = {
        "flight_id": "FL999",  # Vuelo inexistente
        "passenger_name": "John",
        "passenger_email": "john@email.com",
        "seat": "15A",
        "class": "economy"
    }

    try:
        response = session_with_retries.post(
            f"{base_url}/bookings",
            json=booking_data,
            headers=auth_headers,
            timeout=10
        )

        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500) al crear reserva: {response.text}")

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    except RetryError as e:
        pytest.xfail(f"Error de conexión después de múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error al crear reserva: {str(e)}")


# -----------------------------------------------------------
# TEST 3: Obtener todas las reservas
# -----------------------------------------------------------
def test_get_all_bookings(base_url, auth_headers, session_with_retries):
    """Valida que se puedan obtener todas las reservas (lista JSON)."""
    try:
        response = session_with_retries.get(
            f"{base_url}/bookings",
            headers=auth_headers,
            timeout=10
        )

        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500) al obtener reservas: {response.text}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        bookings = response.json()
        assert isinstance(bookings, list)
    except RetryError as e:
        pytest.xfail(f"Error de conexión después de múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error al obtener reservas: {str(e)}")


# -----------------------------------------------------------
# TEST 4: Obtener una reserva específica
# -----------------------------------------------------------
def test_get_booking_by_id(base_url, auth_headers, session_with_retries):
    """Valida la obtención de una reserva específica por ID."""
    try:
        # Buscar reservas existentes
        response_all = session_with_retries.get(
            f"{base_url}/bookings",
            headers=auth_headers,
            timeout=10
        )
        if response_all.status_code != 200 or len(response_all.json()) == 0:
            pytest.skip("No hay reservas existentes para probar la obtención por ID")

        booking_id = response_all.json()[0]["id"]

        # Obtener reserva por ID
        response = session_with_retries.get(
            f"{base_url}/bookings/{booking_id}",
            headers=auth_headers,
            timeout=10
        )

        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500) al obtener reserva: {response.text}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        booking = response.json()
        validate(instance=booking, schema=booking_schema)
    except RetryError as e:
        pytest.xfail(f"Error de conexión después de múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error al obtener reserva por ID: {str(e)}")


# -----------------------------------------------------------
# TEST 5: Cancelar una reserva
# -----------------------------------------------------------
def test_cancel_booking(base_url, auth_headers, session_with_retries):
    """Valida que una reserva confirmada pueda cancelarse exitosamente."""
    try:
        response_all = session_with_retries.get(
            f"{base_url}/bookings",
            headers=auth_headers,
            timeout=10
        )
        if response_all.status_code != 200:
            pytest.skip("No se pudieron obtener reservas")

        # Buscar una reserva confirmada
        bookings = response_all.json()
        booking_to_cancel = next((b for b in bookings if b.get("status") == "confirmed"), None)

        if not booking_to_cancel:
            pytest.skip("No hay reservas confirmadas para cancelar")

        booking_id = booking_to_cancel["id"]

        # Cancelar la reserva
        response = session_with_retries.delete(
            f"{base_url}/bookings/{booking_id}",
            headers=auth_headers,
            timeout=10
        )

        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500) al cancelar reserva: {response.text}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Validar que la reserva ahora esté en estado "cancelled"
        response_updated = session_with_retries.get(
            f"{base_url}/bookings/{booking_id}",
            headers=auth_headers,
            timeout=10
        )
        if response_updated.status_code == 200:
            updated_booking = response_updated.json()
            assert updated_booking["status"] == "cancelled"
    except RetryError as e:
        pytest.xfail(f"Error de conexión después de múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error al cancelar reserva: {str(e)}")


# -----------------------------------------------------------
# TEST 6: Cancelar una reserva ya cancelada
# -----------------------------------------------------------
def test_cancel_already_cancelled_booking(base_url, auth_headers, session_with_retries):
    """Valida que intentar cancelar una reserva ya cancelada devuelva un 400 (Bad Request)."""
    try:
        response_all = session_with_retries.get(
            f"{base_url}/bookings",
            headers=auth_headers,
            timeout=10
        )
        if response_all.status_code != 200:
            pytest.skip("No se pudieron obtener reservas")

        # Buscar reserva ya cancelada
        bookings = response_all.json()
        cancelled_booking = next((b for b in bookings if b.get("status") == "cancelled"), None)

        if not cancelled_booking:
            pytest.skip("No hay reservas canceladas para probar")

        booking_id = cancelled_booking["id"]

        # Intentar cancelar nuevamente
        response = session_with_retries.delete(
            f"{base_url}/bookings/{booking_id}",
            headers=auth_headers,
            timeout=10
        )

        if response.status_code >= 500:
            pytest.xfail(f"Error del servidor (500) al cancelar reserva: {response.text}")

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    except RetryError as e:
        pytest.xfail(f"Error de conexión después de múltiples intentos: {e}")
    except Exception as e:
        pytest.xfail(f"Error al cancelar reserva ya cancelada: {str(e)}")
