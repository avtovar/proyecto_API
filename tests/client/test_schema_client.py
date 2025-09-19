import pytest
import os
import sys

# Añadir el directorio raíz del proyecto al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api_client import APIClient, LOGIN_SCHEMA, ERROR_SCHEMA, SUCCESS_SCHEMA


def test_login_schema():
    """Test que verifica que el login sigue el esquema correcto"""
    client = APIClient()

    # Realizar login
    response = client.login("admin@demo.com", "admin123")

    # Verificar que la respuesta coincide con el esquema
    assert "access_token" in response
    assert response["token_type"] == "bearer"
    assert isinstance(response["access_token"], str)


def test_error_schema():
    """Test que verifica el esquema de error con credenciales inválidas"""
    client = APIClient()

    # Intentar login con credenciales incorrectas
    with pytest.raises(Exception) as exc_info:
        client.login("invalid@user.com", "wrongpassword")

    # Verificar que el mensaje de error contiene información útil
    assert "Login failed" in str(exc_info.value)


def test_success_schema():
    """Test que verifica el esquema de éxito para otras operaciones"""
    client = APIClient()

    # Primero hacer login para obtener token
    client.login("admin@demo.com", "admin123")

    # Ejemplo de otra operación (ajusta según tu API)
    response = client.api_request("GET", "/flights")

    # Verificar que la respuesta es exitosa
    assert response.status_code == 200

    # Si la respuesta es JSON, verificar su estructura
    if response.headers.get("Content-Type") == "application/json":
        data = response.json()
        # Aquí podrías añadir validaciones específicas para el esquema de vuelos
        assert isinstance(data, list) or isinstance(data, dict)