import requests
import pytest
from jsonschema import validate

# Esquema esperado para un usuario
user_schema = {
    "type": "object",
    "required": ["id", "email", "full_name", "role"],
    "properties": {
        "id": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "full_name": {"type": "string"},
        "role": {"type": "string", "enum": ["passenger", "admin"]}
    },
    "additionalProperties": False
}


@pytest.fixture
def test_user(base_url, auth_headers):
    """Fixture para crear un usuario de prueba"""
    user_data = {
        "email": "alondra.tovar@airline.com",
        "password": "Alon12345",
        "full_name": "Alondra Tovar",
        "role": "admin"
    }


    response = requests.post(
        f"{base_url}/users/",
        json=user_data,
        headers=auth_headers
    )
    response.raise_for_status()

    yield response.json()

    # Cleanup: eliminar usuario después de la prueba
    user_id = response.json()["id"]
    requests.delete(f"{base_url}/users/{user_id}", headers=auth_headers)


def test_create_user_schema(test_user):
    """Valida que el usuario creado cumpla con el esquema JSON esperado."""
    validate(instance=test_user, schema=user_schema)


def test_get_all_users(base_url, auth_headers):
    """
    Obtiene todos los usuarios de la API en bloques (paginación).
    Verifica que devuelve una lista de usuarios con id y email válidos.
    """
    limit = 10
    skip = 0
    results = []

    while True:
        r = requests.get(
            f"{base_url}/users/",
            headers=auth_headers,
            params={"skip": skip, "limit": limit},
            timeout=5
        )
        r.raise_for_status()
        users_list = r.json()

        if not users_list:
            break

        results.extend(users_list)
        skip += limit

    # Validaciones
    assert isinstance(results, list)
    if results:
        assert "id" in results[0]
        assert "email" in results[0]