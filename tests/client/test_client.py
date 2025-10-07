import requests
import time
import os
import jsonschema
from jsonschema import validate

# ================================================================
# Configuración global desde variables de entorno (con valores por defecto)
# ================================================================
BASE = os.getenv("BASE_URL", "http://localhost:8000")   # URL base de la API
RETRIES = int(os.getenv("API_RETRIES", "3"))            # Cantidad de reintentos
TIMEOUT = int(os.getenv("API_TIMEOUT", "5"))            # Tiempo máximo por request (segundos)



# ================================================================
# Esquemas de validación JSON (contratos de la API)
# ================================================================
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
        "detail": {"type": "string"},   # Mensaje detallado de error
        "error": {"type": "string"},    # Tipo de error
        "message": {"type": "string"}   # Mensaje legible para el usuario
    },
    "additionalProperties": True        # Puede contener más campos
}

SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string"},  # Mensaje de éxito
        "id": {"type": "string"},       # ID generado (si aplica)
        "status": {"type": "string"}    # Estado del recurso creado/actualizado
    },
    "additionalProperties": True
}

# ================================================================
# Clase principal: APIClient
# ================================================================
class APIClient:
    """Cliente unificado para interactuar con la API de la aerolínea con validación de esquemas"""

    def __init__(self, base_url=BASE):
        self.base_url = base_url
        # Se reutiliza el token si ya existe en variables de entorno
        self.token = os.getenv("API_TOKEN")

    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    def api_request(self, method, path, validate_schema=None, **kwargs):
        """
        Realiza una solicitud HTTP a la API con:
        - Reintentos automáticos en caso de error de red
        - Manejo automático de token de autenticación
        - Validación opcional contra un esquema JSON
        """
        url = f"{self.base_url}{path}"

        for i in range(RETRIES):
            try:
                # Agregar encabezado Authorization si hay token
                headers = kwargs.get("headers", {})
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                    kwargs["headers"] = headers

                # Hacer la solicitud HTTP
                resp = requests.request(method, url, timeout=TIMEOUT, **kwargs)

                # Si es respuesta válida (<500) o último intento, procesar
                if resp.status_code < 500 or i == RETRIES - 1:
                    try:
                        data = resp.json()
                        # Guardar token si la respuesta contiene "access_token"
                        if "access_token" in data:
                            self.token = data["access_token"]
                            os.environ["API_TOKEN"] = self.token
                            print("Token guardado en variable de entorno: API_TOKEN")
                    except ValueError:
                        pass  # Respuesta no es JSON (ej: HTML de error)

                    # Validar contra esquema si se indicó
                    if validate_schema and 200 <= resp.status_code < 300:
                        self.validate_response(resp, validate_schema)

                    return resp

            except requests.exceptions.RequestException as e:
                # Último intento fallido -> lanzar excepción
                if i == RETRIES - 1:
                    raise e

            # Espera exponencial (1s, 2s, 4s…)
            time.sleep(1 << i)

    # ------------------------------------------------------------
    def login(self, username, password):
        """
        Inicia sesión en la API.
        - Envía usuario y contraseña
        - Valida la respuesta contra LOGIN_SCHEMA
        - Guarda el token en memoria y en variables de entorno
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
            # Si no es éxito, validar contra ERROR_SCHEMA para obtener más detalle
            try:
                error_data = self.validate_response(response, ERROR_SCHEMA)
                raise Exception(f"Login failed: {response.status_code} - {error_data}")
            except:
                raise Exception(f"Login failed: {response.status_code} - {response.text}")


# ================================================================
# Función auxiliar (para uso sin instanciar la clase)
# ================================================================
def api_request(method, path, validate_schema=None, **kwargs):
    """Función global para hacer requests sin necesidad de crear una instancia"""
    client = APIClient()
    return client.api_request(method, path, validate_schema=validate_schema, **kwargs)


# ================================================================
# Ejemplo de uso (ejecutar directamente el archivo)
# ================================================================
if __name__ == "__main__":
    # ----------------------
    # Uso con la función global
    # ----------------------
    try:
        login_resp = api_request(
            "POST",
            "/auth/login",
            validate_schema=LOGIN_SCHEMA,
            data={
                "username": "admin@demo.com",
                "password": "admin123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print("Login exitoso!")
        print("Token:", os.environ.get("API_TOKEN"))

    except Exception as e:
        print("Error en login:", e)

    # ----------------------
    # Uso con la clase APIClient
    # ----------------------
    try:
        client = APIClient()
        login_data = client.login("admin@demo.com", "admin123")
        print("Login status (clase):", login_data)

    except Exception as e:
        print("Error en login con clase:", e)
