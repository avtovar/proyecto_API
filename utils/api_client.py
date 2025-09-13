import requests, time, os

BASE = os.getenv("BASE_URL", "http://localhost:8000")  # valor por defecto opcional
RETRIES = 3

def api_request(method, path, **kwargs):
    url = f"{BASE}{path}"
    for i in range(RETRIES):
        try:
            resp = requests.request(method, url, timeout=5, **kwargs)
            if resp.status_code < 500 or i == RETRIES - 1:
                # Si la respuesta contiene un token lo guardamos en entorno
                try:
                    data = resp.json()
                    if "access_token" in data:
                        os.environ["API_TOKEN"] = data["access_token"]
                        print("Token guardado en variable de entorno: API_TOKEN")
                except ValueError:
                    pass  # no es JSON válido
                return resp
        except requests.exceptions.RequestException as e:
            if i == RETRIES - 1:
                raise e
        time.sleep(1 << i)

# Ejemplo de uso: login
if __name__ == "__main__":
    login_resp = api_request(
        "POST",
        "/auth/login",
        data={
            "username": "admin@demo.com",
            "password": "admin123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print("Login status:", login_resp.status_code)
    print("Respuesta:", login_resp.text)
