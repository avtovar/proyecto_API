# Esquemas de validación JSON para pruebas

airport_schema = {
    "type": "object",
    "required": ["iata_code", "city", "country"],
    "properties": {
        "iata_code": {"type": "string", "minLength": 3, "maxLength": 3},
        "city": {"type": "string"},
        "country": {"type": "string"},
    },
    "additionalProperties": False
}

airline_schema = {
    "type": "object",
    "required": ["id", "name", "country"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "country": {"type": "string"},
        "logo": {"type": "string"},
        "slogan": {"type": "string"},
        "head_quaters": {"type": "string"},
        "website": {"type": "string"},
        "established": {"type": "string", "format": "date"},
    },
    "additionalProperties": True
}