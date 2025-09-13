import requests
from jsonschema import validate

# 🔹 Esquema esperado para un usuario
user_schema = {
    "type": "object",
    "required": ["id", "email", "full_name", "role"],
    "properties": {
        "id": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "full_name": {"type": "string"},
        "role": {"type": "string", "enum": ["passenger", "admin"]}
    },
    "additionalProperties": True
}


def test_create_user_schema(user):
    """Valida que el usuario creado cumpla con el esquema JSON esperado."""
    validate(instance=user, schema=user_schema)


def test_get_all_users(base_url, auth_headers, limit=10):
    """
    Obtiene todos los usuarios de la API en bloques (paginación).
    Verifica que devuelve una lista de usuarios con id y email válidos.
    """
    skip = 0
    results = []

    while True:
        r = requests.get(
            f"{base_url}/users/",
            headers=auth_headers,        # 🔹 Se añade token de autenticación
            params={"skip": skip, "limit": limit},
            timeout=5
        )
        r.raise_for_status()
        users_list = r.json()

        if not users_list:
            break

        results.extend(users_list)
        skip += limit

    # 🔹 Validaciones
    assert isinstance(results, list)
    if results:
        assert "id" in results[0]
        assert "email" in results[0]
