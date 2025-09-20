"""
Módulo: create_support_user.py
--------------------------------
Este script permite crear un **usuario de soporte (admin)** en la API de Airline Automation 
utilizando un flujo autenticado con credenciales de administrador. 

Se conecta a los endpoints de autenticación y creación de usuarios para registrar 
un nuevo usuario con rol de administrador. 

Requisitos previos:
- Tener configurado un archivo `.env` con las variables:
    BASE_URL   → URL base de la API
    ADMIN_USER → Usuario administrador
    ADMIN_PASS → Contraseña administrador
"""

import requests
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env
load_dotenv()

# Configuración de endpoints principales
URL = os.getenv("BASE_URL", "https://cf-automation-airline-api.onrender.com")
AUTH_LOGIN = "/auth/login/"
AUTH_SIGNUP = "/users/"

def get_admin_token():
    """
    Realiza login con credenciales de administrador y retorna un token JWT.

    Returns:
        str: token de acceso válido para autenticación en la API.

    Raises:
        Exception: si la API devuelve un error de autenticación.
    """
    admin_data = {
        "username": os.getenv("ADMIN_USER", "admin@demo.com"),
        "password": os.getenv("ADMIN_PASS", "admin123")
    }

    r = requests.post(URL + AUTH_LOGIN, data=admin_data)
    if r.status_code == 200:
        return r.json()["access_token"]
    else:
        raise Exception(f"Error al obtener token: {r.status_code} - {r.text}")


def create_support_user():
    """
    Crea un usuario de soporte (rol admin) utilizando el token de administrador.

    Returns:
        Response: objeto de respuesta HTTP de la API (requests.Response).
    """
    support_user_data = {
        "email": "alondra.tovar@airline.com",
        "password": "Alon12345",
        "full_name": "Alondra Tovar",
        "role": "admin"   # se define explícitamente el rol
    }

    token = get_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",  # autenticación con JWT
        "Content-Type": "application/json"
    }

    r = requests.post(URL + AUTH_SIGNUP, json=support_user_data, headers=headers)
    return r


if __name__ == "__main__":
    """
    Ejecución directa del script.
    Intenta crear un usuario de soporte y muestra el resultado por consola.
    """
    response = create_support_user()
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
