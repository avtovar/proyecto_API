import random
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


def test_create_user_schema(test_user):
    """Valida que el usuario creado cumpla con el esquema JSON esperado."""
    validate(instance=test_user, schema=user_schema)


def test_get_all_users(base_url, auth_headers, session_with_retries):
    """
    Obtiene todos los usuarios de la API en bloques (paginación).
    Verifica que devuelve una lista de usuarios con id y email válidos.
    """
    limit = 10
    skip = 0
    results = []

    while True:
        r = session_with_retries.get(
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


def test_delete_user_alondra(base_url, auth_headers, session_with_retries):
    """
    Crea o busca a 'Alondra Tovar' y luego lo elimina.
    """
    # Buscar si ya existe
    r = session_with_retries.get(f"{base_url}/users/", headers=auth_headers, timeout=5)
    r.raise_for_status()
    users = r.json()
    alondra = next((u for u in users if u.get("full_name") == "Alondra Tovar"), None)

    if not alondra:
        user_data = {
            "email": f"alondra.{random.randint(1000,9999)}@airline.com",
            "password": "Alon12345",
            "full_name": "Alondra Tovar",
            "role": "admin"
        }
        create_resp = session_with_retries.post(
            f"{base_url}/users/",
            json=user_data,
            headers=auth_headers,
            timeout=5
        )
        create_resp.raise_for_status()
        alondra = create_resp.json()

    # Eliminar usuario encontrado o recién creado
    user_id = alondra["id"]
    delete_response = session_with_retries.delete(
        f"{base_url}/users/{user_id}",
        headers=auth_headers,
        timeout=5
    )
    assert delete_response.status_code in [200, 204], f"Error al eliminar usuario: {delete_response.text}"
