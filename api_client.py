import requests
import time
import os
import jsonschema
from jsonschema import validate

BASE = os.getenv("BASE_URL", "http://localhost:8000")
RETRIES = int(os.getenv("API_RETRIES", "3"))
TIMEOUT = int(os.getenv("API_TIMEOUT", "5"))

# Esquemas de validación
LOGIN_SCHEMA = {
    "type": "object",
    "required": ["access_token", "token_type"],
    "properties": {
        "access_token": {"type": "string"},
        "token_type": {"type": "string", "enum": ["bearer"]}
    },
    "additionalProperties": False
}

ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {"type": "string"},
        "error": {"type": "string"},
        "message": {"type": "string"}
    },
    "additionalProperties": True
}

SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string"},
        "id": {"type": "string"},
        "status": {"type": "string"}
    },
    "additionalProperties": True
}


class APIClient:
    """Cliente unificado para interactuar con la API de la aerolínea con validación de esquemas"""

    def __init__(self, base_url=BASE):
        self.base_url = base_url
        self.token = os.getenv("API_TOKEN")

    def validate_response(self, response, schema):
        """Valida una respuesta JSON contra un esquema específico"""
        try:
            data = response.json()
            validate(instance=data, schema=schema)
            return data
        except jsonschema.ValidationError as e:
            raise Exception(f"Validación de esquema falló: {e}")
        except ValueError as e:
            raise Exception(f"Respuesta JSON inválida: {e}")

    def api_request(self, method, path, validate_schema=None, **kwargs):
        """Realiza una solicitud a la API con reintentos, gestión de tokens y validación opcional"""
        url = f"{self.base_url}{path}"

        for i in range(RETRIES):
            try:
                # Agregar token si está disponible
                headers = kwargs.get("headers", {})
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                    kwargs["headers"] = headers

                resp = requests.request(method, url, timeout=TIMEOUT, **kwargs)

                # Si es una respuesta exitosa o el último intento
                if resp.status_code < 500 or i == RETRIES - 1:
                    # Guardar token si está en la respuesta
                    try:
                        data = resp.json()
                        if "access_token" in data:
                            self.token = data["access_token"]
                            os.environ["API_TOKEN"] = self.token
                    except ValueError:
                        pass  # no es JSON válido

                    # Validar contra esquema si se especificó
                    if validate_schema and 200 <= resp.status_code < 300:
                        self.validate_response(resp, validate_schema)

                    return resp

            except requests.exceptions.RequestException as e:
                if i == RETRIES - 1:
                    raise e

            time.sleep(1 << i)  # Espera exponencial

    def login(self, username, password):
        """Iniciar sesión en la API con validación de esquema"""
        response = self.api_request(
            "POST",
            "/auth/login",
            validate_schema=LOGIN_SCHEMA,
            data={
                "username": username,
                "password": password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code == 200:
            return response.json()
        else:
            # Validar si es un error
            try:
                error_data = self.validate_response(response, ERROR_SCHEMA)
                raise Exception(f"Login failed: {response.status_code} - {error_data}")
            except:
                raise Exception(f"Login failed: {response.status_code} - {response.text}")


# Función de conveniencia para uso simple
def api_request(method, path, validate_schema=None, **kwargs):
    """Función global para hacer requests sin necesidad de crear una instancia"""
    client = APIClient()
    return client.api_request(method, path, validate_schema=validate_schema, **kwargs)