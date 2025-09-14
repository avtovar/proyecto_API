from dotenv import load_dotenv
import os

load_dotenv()

# Configuración de la API
BASE_URL = os.getenv("BASE_URL", "https://cf-automation-airline-api.onrender.com")
ADMIN_USER = os.getenv("ADMIN_USER", "admin@demo.com")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "admin123")

# Configuración de pruebas
TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))