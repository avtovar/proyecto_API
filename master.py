import requests
import json
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv

# 📌 Cargar variables de entorno
load_dotenv()

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AirlineAPIClient:
    """Cliente para interactuar con la API de automatización de aerolínea"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.auth_token = None
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "AirlineAPIClient/1.0"
        }

    def _build_url(self, endpoint: str) -> str:
        """Construye la URL completa para un endpoint"""
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Maneja la respuesta de la API y devuelve los datos JSON"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP: {e}")
            logger.error(f"Respuesta: {response.text}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON: {e}")
            logger.error(f"Respuesta: {response.text}")
            raise

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Inicia sesión en la API y guarda el token de autenticación"""
        endpoint = "auth/login/"
        url = self._build_url(endpoint)

        login_data = {"username": username, "password": password}

        try:
            response = requests.post(url, json=login_data, headers=self.headers, timeout=5)
            result = self._handle_response(response)

            # Guardar el token para futuras solicitudes
            if "access_token" in result:
                self.auth_token = result["access_token"]
                self.headers["Authorization"] = f"Bearer {self.auth_token}"
                logger.info("Login exitoso")

            return result
        except Exception as e:
            logger.error(f"Error en login: {e}")
            raise

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo usuario"""
        endpoint = "users/"
        url = self._build_url(endpoint)

        try:
            response = requests.post(url, json=user_data, headers=self.headers, timeout=5)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            raise

    def list_users(self, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """Obtiene la lista de usuarios"""
        endpoint = f"users?skip={skip}&limit={limit}"
        url = self._build_url(endpoint)

        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Error obteniendo usuarios: {e}")
            raise


# -------------------- CONFIG --------------------
BASE_URL = os.getenv("BASE_URL", "https://cf-automation-airline-api.onrender.com")

ADMIN_CREDENTIALS = {
    "username": os.getenv("ADMIN_USER"),
    "password": os.getenv("ADMIN_PASS")
}

SUPPORT_USER_DATA = {
    "email": "helios123@airline.com",
    "password": "helios12345",
    "full_name": "Helios Barrera",
    "role": "admin"
}


def master():
    """Función principal para demostrar el uso del cliente API"""
    client = AirlineAPIClient(BASE_URL)

    try:
        # Iniciar sesión como administrador
        login_result = client.login(**ADMIN_CREDENTIALS)
        logger.info(f"Login exitoso: {login_result.get('message', 'Sin mensaje')}")

        # Crear usuario de soporte
        user_creation_result = client.create_user(SUPPORT_USER_DATA)
        logger.info(f"Usuario creado: {user_creation_result}")

        # Listar usuarios
        users = client.list_users()
        logger.info(f"Usuarios en el sistema: {len(users.get('users', []))}")

    except Exception as e:
        logger.error(f"Error en la ejecución: {e}")


if __name__ == "__main__":
    master()
