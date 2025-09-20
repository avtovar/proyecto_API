import requests
import time
import os
import jsonschema
from jsonschema import validate

# ======================================================
# Configuración base del cliente API
# ======================================================

# URL base de la API (puede configurarse como variable de entorno)
BASE = os.getenv("BASE_URL", "http://localhost:8000")

# Número máximo de reintentos en caso de error de red/servidor
RETRIES = int(os.getenv("API_RETRIES", "3"))

# Tiempo máximo de espera para cada request (en segundos)
TIMEOUT = int(os.getenv("API_TIMEOUT", "5"))

# ======================================================
# Esquemas de validación JSON
# ======================================================
# Estos esquemas definen la estructura esperada de las
# respuestas de la API. Se validan automáticamente con
# la librería `jsonschema`.
# ======================================================

LOGIN_SCHEMA = {
    "type": "object",
    "required": ["access_token", "token_type"],
    "properties": {
        "access_token": {"type": "string"},         # Token JWT
        "token_type": {"type": "string", "enum": ["bearer"]}  # Tipo de token
    },
    "additionalProperties": False  # No se aceptan otros campos
}

ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {"type": "string"},   # Mensaje de detalle
        "error": {"type": "string"},    # Código de error
        "message": {"type": "string"}   # Mensaje adicional
    },
    "additionalProperties": True  # Puede contener más campos (ej. `status_code`)
}

SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string"},  # Mensaje de éxito
        "id": {"type": "string"},       # Identificador del recurso creado/modificado
        "status": {"type": "string"}    # Estado (ej. "ok", "completed")
    },
    "additionalProperties": True  # Puede contener más propiedades
}

# ======================================================
# Clase principal del cliente de la API
# ======================================================

class APIClient:
    """Cliente unificado para interactuar con la API de la aerolínea con validación de esquemas"""

    def __init__(self, base_url=BASE):
        """
        Inicializa el cliente API.

        Args:
            base_url (str): URL base de la API. Por defecto usa la variable de entorno BASE_URL.
        """
        self.base_url = base_url
        # Se puede pasar un token existente mediante la variable de entorno API_TOKEN
        self.token = os.getenv("API_TOKEN")

    # --------------------------------------------------
    # Validación de respuestas
    # --------------------------------------------------
    def validate_response(self, response, schema):
        """
        Valida que la respuesta JSON cumpla con el esquema esperado.

        Args:
            response (requests.Response): Respuesta de la API.
            schema (dict): Esquema JSON Schema contra el cual validar.

        Returns:
            dict: Respuesta JSON validada.

        Raises:
            Exception: Si la validación falla o la respuesta no es JSON válido.
        """
        try:
            data = response.json()
            validate(instance=data, schema=schema)
            return data
        except jsonschema.ValidationError as e:
            raise Exception(f"Validación de esquema falló: {e}")
        except ValueError as e:
            raise Exception(f"Respuesta JSON inválida: {e}")

    # --------------------------------------------------
    # Método genérico para requests
    # --------------------------------------------------
    def api_request(self, method, path, validate_schema=None, **kwargs):
        """
        Realiza una solicitud HTTP a la API con reintentos, manejo de token y validación opcional.

        Args:
            method (str): Método HTTP (GET, POST, PUT, DELETE).
            path (str): Ruta de la API (ej. "/flights").
            validate_schema (dict, optional): Esquema para validar la respuesta si es exitosa.
            **kwargs: Parámetros adicionales que se pasan a requests.request().

        Returns:
            requests.Response: Objeto de respuesta HTTP.
        """
        url = f"{self.base_url}{path}"

        for i in range(RETRIES):
            try:
                # Agregar encabezado de autorización si hay token disponible
                headers = kwargs.get("headers", {})
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                    kwargs["headers"] = headers

                # Realizar la request HTTP
                resp = requests.request(method, url, timeout=TIMEOUT, **kwargs)

                # Si es exitosa (<500) o estamos en el último intento, procesar
                if resp.status_code < 500 or i == RETRIES - 1:
                    # Guardar token si está en la respuesta
                    try:
                        data = resp.json()
                        if "access_token" in data:
                            self.token = data["access_token"]
                            os.environ["API_TOKEN"] = self.token
                    except ValueError:
                        pass  # respuesta no es JSON válido

                    # Validar contra esquema si corresponde
                    if validate_schema and 200 <= resp.status_code < 300:
                        self.validate_response(resp, validate_schema)

                    return resp

            except requests.exceptions.RequestException as e:
                # Si fue el último intento, propagar excepción
                if i == RETRIES - 1:
                    raise e

            # Espera exponencial: 1s, 2s, 4s, etc.
            time.sleep(1 << i)

    # --------------------------------------------------
    # Método de login
    # --------------------------------------------------
    def login(self, username, password):
        """
        Realiza login en la API y guarda el token en el cliente.

        Args:
            username (str): Usuario/correo.
            password (str): Contraseña.

        Returns:
            dict: Respuesta JSON con el token de acceso.

        Raises:
            Exception: Si el login falla o la respuesta no cumple esquema.
        """
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
            # Validar como error si corresponde
            try:
                error_data = self.validate_response(response, ERROR_SCHEMA)
                raise Exception(f"Login failed: {response.status_code} - {error_data}")
            except:
                raise Exception(f"Login failed: {response.status_code} - {response.text}")

# ======================================================
# Función global de conveniencia
# ======================================================

def api_request(method, path, validate_schema=None, **kwargs):
    """
    Función global para hacer requests sin necesidad de instanciar APIClient.

    Args:
        method (str): Método HTTP.
        path (str): Ruta de la API.
        validate_schema (dict, optional): Esquema para validar respuesta.
        **kwargs: Parámetros adicionales para requests.

    Returns:
        requests.Response: Objeto de respuesta.
    """
    client = APIClient()
    return client.api_request(method, path, validate_schema=validate_schema, **kwargs)
