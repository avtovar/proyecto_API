# Proyecto_API

## Descripción General
Este proyecto implementa la automatización de pruebas para la API de la aerolínea disponible en:

[Airline Demo API - Swagger UI](https://cf-automation-airline-api.onrender.com/docs)

La API proporciona endpoints para gestionar vuelos, reservaciones y operaciones relacionadas con una aerolínea.

## Características de la API
### Endpoints Principales
- **Vuelos**: Gestión de información de vuelos disponibles
- **Reservaciones**: Creación y gestión de reservas de pasajeros
- **Autenticación**: Sistema de seguridad para acceso a endpoints protegidos
- **Estados**: Verificación del status del servicio

### Tecnologías Utilizadas
- **Framework**: FastAPI (basado en OpenAPI/Swagger)
- **Documentación**: Interfaz Swagger integrada
- **Autenticación**: JWT (JSON Web Tokens)
- **Formato de datos**: JSON

## Alcance de la Automatización
### Casos de Prueba Cubiertos
- **Pruebas de Health Check**
  - Verificación de disponibilidad del servicio
  - Validación de respuesta y tiempos de respuesta

- **Pruebas de Endpoints Públicos**
  - Consulta de vuelos disponibles
  - Obtención de información de aeropuertos

- **Pruebas de Endpoints Protegidos**
  - Creación de reservaciones
  - Gestión de usuarios
  - Autenticación y autorización

- **Pruebas de Validación de Datos**
  - Esquemas de respuesta
  - Códigos de estado HTTP
  - Manejo de errores

### Herramientas de Automatización
- **Lenguaje**: Python
- **Framework**: Pytest
- **Librerías**: Requests, Pydantic (para validación de esquemas)
- **Gestión de variables**: Environment variables
- **Reportes**: pytest-html

## Configuración del Entorno
1. Crear un entorno virtual: `python -m venv venv`
2. Activar el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
3. Instalar dependencias: `pip install -r requirements.txt`
4. Configurar variables de entorno en archivo `.env`

## Ejecución de Pruebas
- Ejecutar todas las pruebas: `pytest -v`
- Ejecutar con reporte HTML: `pytest --html=report.html`