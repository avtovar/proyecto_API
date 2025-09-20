# test_schema_flights.py
# ======================================================
# Este archivo define un esquema de validación JSON Schema
# para objetos de tipo "flight" (vuelo).
# Se utiliza para asegurar que las respuestas de la API
# cumplan con la estructura esperada al manejar datos de vuelos.
# ======================================================

# Esquema de validación JSON para vuelos
flight_schema = {
    "type": "object",  # El objeto debe ser un JSON de tipo objeto
    "required": [
        "id",           # Identificador único del vuelo
        "name",         # Nombre del vuelo (ej. "AR1234")
        "from",         # Código IATA del aeropuerto de origen (3 letras)
        "to",           # Código IATA del aeropuerto de destino (3 letras)
        "departure",    # Hora de salida en formato válido
        "arrival",      # Hora de llegada en formato válido
        "duration",     # Duración del vuelo en horas/minutos
        "stops",        # Número de escalas (entero, mínimo 0)
        "price",        # Precio del vuelo (número positivo)
        "airline_id"    # Identificador de la aerolínea
    ],
    "properties": {
        "id": {"type": "string"},  # ID del vuelo, en formato string (UUID o similar)
        "name": {"type": "string"},  # Nombre/código del vuelo
        "from": {
            "type": "string",
            "minLength": 3,
            "maxLength": 3
        },  # Código IATA de origen (ej. "EZE")
        "to": {
            "type": "string",
            "minLength": 3,
            "maxLength": 3
        },  # Código IATA de destino (ej. "MIA")
        "departure": {
            "type": "string",
            "format": "time"
        },  # Hora de salida (ej. "14:30")
        "arrival": {
            "type": "string",
            "format": "time"
        },  # Hora de llegada (ej. "20:45")
        "duration": {"type": "number"},  # Duración del vuelo en horas o minutos (ej. 8.5)
        "stops": {
            "type": "integer",
            "minimum": 0
        },  # Número de escalas (0 = vuelo directo)
        "price": {
            "type": "number",
            "minimum": 0
        },  # Precio en USD u otra moneda (no negativo)
        "airline_id": {"type": "string"}  # Identificador de la aerolínea propietaria del vuelo
    },
    "additionalProperties": False  # No se permiten propiedades extra no definidas
}
