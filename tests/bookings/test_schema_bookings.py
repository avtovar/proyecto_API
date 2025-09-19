# Esquema de validación JSON para reservas
booking_schema = {
    "type": "object",
    "required": ["id", "flight_id", "passenger_name", "passenger_email", "seat", "class", "status"],
    "properties": {
        "id": {"type": "string"},
        "flight_id": {"type": "string"},
        "passenger_name": {"type": "string"},
        "passenger_email": {"type": "string", "format": "email"},
        "seat": {"type": "string"},
        "class": {"type": "string", "enum": ["economy", "business", "first"]},
        "status": {"type": "string", "enum": ["confirmed", "cancelled"]}
    },
    "additionalProperties": False
}