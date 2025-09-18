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