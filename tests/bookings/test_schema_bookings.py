# ================================================================
# Esquema de validación JSON para reservas en el sistema de aerolíneas
# ================================================================
# Este esquema define cómo debe estructurarse un objeto "booking" (reserva).
# Se utiliza en las pruebas automatizadas con jsonschema para validar
# que las respuestas de la API cumplen con el contrato esperado.
# ================================================================

booking_schema = {
    "type": "object",  # El objeto raíz debe ser de tipo JSON "objeto"
    "required": [
        "id",               # Identificador único de la reserva
        "flight_id",        # ID del vuelo asociado
        "passenger_name",   # Nombre del pasajero
        "passenger_email",  # Email del pasajero
        "seat",             # Asiento asignado
        "class",            # Clase de la reserva (ej: economy)
        "status"            # Estado de la reserva (ej: confirmed)
    ],
    "properties": {
        # Identificador único de la reserva
        "id": {"type": "string"},

        # Relación con el vuelo correspondiente
        "flight_id": {"type": "string"},

        # Nombre completo del pasajero
        "passenger_name": {"type": "string"},

        # Correo electrónico válido del pasajero
        "passenger_email": {"type": "string", "format": "email"},

        # Asiento asignado (ejemplo: "15A")
        "seat": {"type": "string"},

        # Clase de la reserva: solo se permiten estas opciones
        "class": {
            "type": "string",
            "enum": ["economy", "business", "first"]
        },

        # Estado de la reserva: solo puede ser confirmada o cancelada
        "status": {
            "type": "string",
            "enum": ["confirmed", "cancelled"]
        }
    },

    # No se permiten propiedades adicionales más allá de las definidas
    "additionalProperties": False
}
