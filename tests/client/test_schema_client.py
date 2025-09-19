# Esquema de validación para respuestas del cliente API

# Usando la función global
resp = api_request("POST", "/auth/login", validate_schema=LOGIN_SCHEMA, data={...})

# Usando la clase
client = APIClient()
client.login("user", "pass")  # Valida automáticamente con LOGIN_SCHEMA

# Esquema para respuesta de login exitoso
login_schema = {
    "type": "object",
    "required": ["access_token", "token_type"],
    "properties": {
        "access_token": {"type": "string"},
        "token_type": {"type": "string", "enum": ["bearer"]}
    },
    "additionalProperties": False
}

# Esquema para respuesta de error general
error_schema = {
    "type": "object",
    "properties": {
        "detail": {"type": "string"},
        "error": {"type": "string"},
        "message": {"type": "string"}
    },
    "additionalProperties": True
}

# Esquema para respuesta de operación exitosa
success_schema = {
    "type": "object",
    "properties": {
        "message": {"type": "string"},
        "id": {"type": "string"},
        "status": {"type": "string"}
    },
    "additionalProperties": True
}

