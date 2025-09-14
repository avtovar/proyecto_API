import requests
import time
import os

BASE = os.getenv("BASE_URL", "https://cf-automation-airline-api.onrender.com")
RETRIES = int(os.getenv("API_RETRIES", "3"))
TIMEOUT = int(os.getenv("API_TIMEOUT", "5"))


class APIClient:
    """Cliente para interactuar con la API de la aerolínea"""

    def __init__(self, base_url=BASE):
        self.base_url = base_url
        self.token = None

    def api_request(self, method, path, **kwargs):
        """Realiza una solicitud a la API con reintentos"""
        url = f"{self.base_url}{path}"

        for i in range(RETRIES):
            try:
                # Agregar token si está disponible
                if self.token and "headers" in kwargs:
                    kwargs["headers"]["Authorization"] = f"Bearer {self.token}"

                resp = requests.request(method, url, timeout=TIMEOUT, **kwargs)

                # Si es una respuesta exitosa o el último intento
                if resp.status_code < 500 or i == RETRIES - 1:
                    # Guardar token si está en la respuesta
                    try:
                        data = resp.json()
                        if "access_token" in data:
                            self.token = data["access_token"]
                    except ValueError:
                        pass  # no es JSON válido

                    return resp

            except requests.exceptions.RequestException as e:
                if i == RETRIES - 1:
                    raise e

            time.sleep(1 << i)  # Espera exponencial

    def login(self, username, password):
        """Iniciar sesión en la API"""
        response = self.api_request(
            "POST",
            "/auth/login",
            data={
                "username": username,
                "password": password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Login failed: {response.status_code} - {response.text}")


# Ejemplo de uso
if __name__ == "__main__":
    client = APIClient()
    login_resp = client.login("admin@demo.com", "admin123")
    print("Login status:", login_resp)