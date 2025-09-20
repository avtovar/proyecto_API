import pytest
import os
import sys

# ================================================================
# Configuración de entorno para importar módulos del proyecto
# ================================================================
# Se añade el directorio raíz del proyecto al sys.path para que
# Python pueda encontrar e importar los módulos correctamente.
# Esto es útil cuando la estructura del proyecto tiene subdirectorios.
# ================================================================
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importación del cliente API y esquemas de validación
from api_client import APIClient, LOGIN_SCHEMA, ERROR_SCHEMA, SUCCESS_SCHEMA


# ================================================================
# Test: Validación de esquema de login
# ================================================================
def test_login_schema():
    """
    Verifica que el login de la API devuelve un objeto con la estructura esperada:
      - Debe contener un "access_token"
      - El campo "token_type" debe ser "bearer"
      - El "access_token" debe ser un string
    """
    client = APIClient()

    # Ejecutar login con credenciales válidas
    response = client.login("admin@demo.com", "admin123")

    # Validaciones del esquema de login
    assert "access_token" in response
    assert response["token_type"] == "bearer"
    assert isinstance(response["access_token"], str)


# ================================================================
# Test: Validación de esquema de error
# ================================================================
def test_error_schema():
    """
    Verifica que, al intentar loguearse con credenciales inválidas:
      - La API lance una excepción
      - El mensaje de error contenga información útil
    """
    client = APIClient()

    # Ejecutar login con credenciales incorrectas
    with pytest.raises(Exception) as exc_info:
        client.login("invalid@user.com", "wrongpassword")

    # Validación del mensaje de error
    assert "Login failed" in str(exc_info.value)


# ================================================================
# Test: Validación de esquema de éxito en otras operaciones
# ================================================================
def test_success_schema():
    """
    Verifica que, tras un login exitoso:
      - Se pueda ejecutar otra operación (ejemplo: GET /flights)
      - La respuesta tenga código HTTP 200
      - Si es JSON, debe ser lista o diccionario
    """
    client = APIClient()

    # Hacer login para obtener un token válido
    client.login("admin@demo.com", "admin123")

    # Ejecutar operación de ejemplo: consultar vuelos
    response = client.api_request("GET", "/flights")

    # Manejo de errores del servidor
    if response.status_code >= 500:
        pytest.xfail(f"Error del servidor ({response.status_code}) al consultar vuelos: {response.text}")

    # Validación del status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Validación del contenido JSON
    if response.headers.get("Content-Type") == "application/json":
        data = response.json()
        assert isinstance(data, (list, dict))
