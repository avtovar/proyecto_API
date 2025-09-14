import requests
import os
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("BASE_URL", "https://cf-automation-airline-api.onrender.com")
AUTH_LOGIN = "/auth/login/"
AUTH_SIGNUP = "/users/"

def get_admin_token():
    """Obtener token de administrador"""
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
    """Crear usuario de soporte para pruebas"""
    support_user_data = {
        "email": "alondra.tovar@airline.com",
        "password": "Alon12345",
        "full_name": "Alondra Tovar",
        "role": "admin"
    }

    token = get_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    r = requests.post(URL + AUTH_SIGNUP, json=support_user_data, headers=headers)
    return r

if __name__ == "__main__":
    response = create_support_user()
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")