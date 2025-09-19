# test_schema_flights.py

flight_schema = {
    "type": "object",
    "required": ["id", "name", "from", "to", "departure", "arrival", "duration", "stops", "price", "airline_id"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "from": {"type": "string", "minLength": 3, "maxLength": 3},
        "to": {"type": "string", "minLength": 3, "maxLength": 3},
        "departure": {"type": "string", "format": "time"},
        "arrival": {"type": "string", "format": "time"},
        "duration": {"type": "number"},
        "stops": {"type": "integer", "minimum": 0},
        "price": {"type": "number", "minimum": 0},
        "airline_id": {"type": "string"}
    },
    "additionalProperties": False
}