# Proyecto_API ✈️

## Descripción General
Este proyecto implementa la **automatización de pruebas** para la **API de la Aerolínea**, disponible en:

👉 [Airline Demo API - Swagger UI](https://cf-automation-airline-api.onrender.com/docs)

La API expone endpoints para gestionar vuelos, aerolíneas, reservas y usuarios, incluyendo autenticación con JWT.

---

## Características de la API
### Endpoints principales
- **Auth** → Login, registro de usuarios, emisión de tokens
- **Flights** → Creación, consulta y filtrado de vuelos
- **Airlines** → Gestión de aerolíneas
- **Airports** → Gestión de aeropuertos
- **Bookings** → Creación, consulta y cancelación de reservas
- **Health** → Verificación del estado del servicio

### Tecnologías utilizadas
- **Backend API**: FastAPI (OpenAPI/Swagger)
- **Autenticación**: JWT
- **Formato de datos**: JSON
- **Framework de testing**: Pytest
- **Cliente HTTP**: Requests con retries automáticos
- **Validación de esquemas**: JSONSchema
- **Reportes**: pytest-html, junit-xml, cobertura

---

## Alcance de la Automatización
### Casos de prueba cubiertos
- **Health Check**
  - Disponibilidad de la API
  - Tiempos de respuesta
- **Autenticación**
  - Login con credenciales válidas
  - Login inválido (errores manejados)
  - Validación de esquemas (`LOGIN_SCHEMA`, `ERROR_SCHEMA`)
- **Usuarios**
  - Creación y eliminación de usuarios de prueba
  - Roles (`passenger`, `admin`)
- **Aeropuertos**
  - Crear, consultar, actualizar y eliminar aeropuertos
  - Validación con `airport_schema`
- **Aerolíneas**
  - Crear y consultar aerolíneas
  - Validación con `airline_schema`
- **Vuelos**
  - Crear vuelos válidos
  - Intentar crear vuelos con aerolíneas inexistentes
  - Consultar todos los vuelos
  - Filtrar por origen/destino
  - Validación con `flight_schema` y `flight_search_schema`
- **Reservas**
  - Crear reservas exitosas
  - Reservar vuelo inexistente
  - Obtener todas las reservas
  - Consultar por ID
  - Cancelar reservas y validar estados
  - Validación con `booking_schema`

---

## Estructura del Proyecto
```bash
Proyecto_API/
│── api_client.py # Cliente unificado con validación de esquemas
│── conftest.py # Configuración global de pytest y fixtures
│── tests/
│ ├── airports/ # Tests de aeropuertos + schemas
│ ├── airlines/ # Tests de aerolíneas + schemas
│ ├── flights/ # Tests de vuelos + schemas
│ ├── bookings/ # Tests de reservas + schemas
│ ├── auth/ # Tests de login/signup
│── .env # Variables de entorno
│── requirements.txt # Dependencias del proyecto
│── pytest.ini # Configuración de pytest
│── .github/workflows/ # CI/CD con GitHub Actions
└── README.md
```

## Configuración del Entorno
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/usuario/Proyecto_API.git
   cd Proyecto_API
   ```

2. Crear entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
   
4. Configurar variables de entorno en .env:
   ```bash
   BASE_URL=https://cf-automation-airline-api.onrender.com
   ADMIN_USER=admin@demo.com
   ADMIN_PASS=admin123
   API_RETRIES=3
   API_TIMEOUT=5I
   ```

## Ejecución de Pruebas
- Ejecutar todas las pruebas:
   ```bash
   pytest -v
   ```

## Ejecutar con reporte HTML:
- Ejecutar todas las pruebas:
   ```bash
   pytest --html=reports/report.html --self-contained-html
   ```
## Ejecutar con cobertura:
- Ejecutar todas las pruebas:
   ```bash
   pytest --cov=api_client --cov=tests --cov-report=html
   ```

## Integración Continua (CI/CD)

Se incluye un workflow de GitHub Actions (ci_api_airline.yaml) que:

1.- Ejecuta los tests en cada push/PR.

2.- Genera reportes HTML, cobertura y JUnit.

3.- Publica resultados como artefactos.

4.- Asegura limpieza de cachés de Python.

Ejemplo:
```bash
     jobs:
      test-api:
       runs-on: ubuntu-latest
       steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
        - run: pip install -r requirements.txt
        - run: pytest -v --html=report.html
   ```

## Gestión de Usuarios de Soporte

El script create_support_user.py permite crear usuarios de soporte (admin) en la API:
   ```bash
      python create_support_user.py
   ```

Este script:

- Obtiene un token de administrador con get_admin_token()

- Crea un usuario admin definido en el payload

- Retorna la respuesta de la API


## pytest.ini
El archivo pytest.ini configura rutas y paths para pytest:
```bash
   [pytest]
   pythonpath = .
   testpaths = tests
```
Opcionalmente se pueden definir marcadores personalizados:
```bash
   markers =
    slow: tests de ejecución lenta
    api: tests de la API
    unit: tests unitarios
    integration: tests de integración
```
## Recursos

- Pruebas en Jira:[Ver TAblero](https://ali-valentin-tovar-morales.atlassian.net/jira/software/projects/ADAA/list)
  
- Confluence: [Resumen](https://ali-valentin-tovar-morales.atlassian.net/wiki/spaces/api/pages/119570436/Resumen+de+Automatizaci+n+API+para+Aerol+nea)
  
## Autor
Ali Valentin Tovar Morales
- QA Automation Tester
- Buenos Aires, Argentina
- ali.v.tovar@gmail.com
- [LinkedIn](www.linkedin.com/in/ali-v-tovar)


Roberto Gamboa López

- QA Automation Tester
- Chiapas, México
- [Tu email]
- LinkedIn

Sergio Solano

- QA Automation Tester
- Chiapas, México
- [Tu email]
- LinkedIn