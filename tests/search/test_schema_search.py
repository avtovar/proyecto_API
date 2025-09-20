# ======================================================
# Esquemas de validación para búsquedas de vuelos
# ======================================================
# Este esquema se utiliza para validar los resultados
# obtenidos en una búsqueda de vuelos.
#
# A diferencia del esquema de vuelos (`flight_schema`),
# aquí se incluye el campo `date`, ya que en las búsquedas
# se espera indicar la fecha del viaje.
# Además, se permite `additionalProperties=True` porque
# las búsquedas suelen traer metadatos adicionales
# (ej. promociones, disponibilidad, etc.).
# ======================================================

flight_search_schema = {
    "type": "object",  # El resultado debe ser un objeto JSON
    "required": [
        "id",           # Identificador único del vuelo
        "name",         # Nombre/código del vuelo
        "from",         # Aeropuerto de origen (IATA)
        "to",           # Aeropuerto de destino (IATA)
        "departure",    # Hora de salida
        "arrival",      # Hora de llegada
        "duration",     # Duración total
        "stops",        # Número de escalas
        "price",        # Precio estimado
        "airline_id"    # ID de la aerolínea
    ],
    "properties": {
        "id": {"type": "string"},  # ID único del vuelo
        "name": {"type": "string"},  # Nombre/código (ej. "AA123")
        "from": {
            "type": "string",
            "minLength": 3,
            "maxLength": 3
        },  # Código IATA origen
        "to": {
            "type": "string",
            "minLength": 3,
            "maxLength": 3
        },  # Código IATA destino
        "departure": {"type": "string"},  # Hora de salida (sin formato fijo)
        "arrival": {"type": "string"},  # Hora de llegada (sin formato fijo)
        "duration": {"type": "number"},  # Duración numérica (ej. 2.5 = 2h30m)
        "stops": {
            "type": "integer",
            "minimum": 0
        },  # Número de escalas, 0 = directo
        "price": {
            "type": "number",
            "minimum": 0
        },  # Precio del vuelo, no negativo
        "airline_id": {"type": "string"},  # Identificador de aerolínea
        "date": {
            "type": "string",
            "format": "date"
        }  # Fecha del vuelo en formato ISO (YYYY-MM-DD)
    },
    "additionalProperties": True  # Se permiten propiedades adicionales
}
