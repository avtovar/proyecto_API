# -----------------------------------------------------------
# Archivo: test_schemas.py
# Descripción:
#   Definición de esquemas JSON Schema utilizados para validar
#   las respuestas de la API en las pruebas automatizadas.
#   Se incluyen los esquemas de:
#     - Aeropuertos (airport_schema)
#     - Aerolíneas (airline_schema)
# -----------------------------------------------------------

# -----------------------------------------------------------
# Esquema de validación para un aeropuerto
# -----------------------------------------------------------
airport_schema = {
    "type": "object",   # La respuesta debe ser un objeto JSON
    "required": ["iata_code", "city", "country"],  # Campos obligatorios
    "properties": {
        "iata_code": {"type": "string", "minLength": 3, "maxLength": 3},  # Código IATA (3 letras)
        "city": {"type": "string"},       # Ciudad asociada al aeropuerto
        "country": {"type": "string"},    # País del aeropuerto
    },
    "additionalProperties": False   # No se permiten otros campos extra
}

# -----------------------------------------------------------
# Esquema de validación para una aerolínea
# -----------------------------------------------------------
airline_schema = {
    "type": "object",   # La respuesta debe ser un objeto JSON
    "required": ["id", "name", "country"],  # Campos obligatorios
    "properties": {
        "id": {"type": "string"},         # Identificador único de la aerolínea
        "name": {"type": "string"},       # Nombre de la aerolínea
        "country": {"type": "string"},    # País de origen
        "logo": {"type": "string"},       # URL del logo de la aerolínea
        "slogan": {"type": "string"},     # Lema o slogan
        "head_quaters": {"type": "string"}, # Sede central (campo opcional)
        "website": {"type": "string"},    # Página web oficial
        "established": {"type": "string", "format": "date"},  # Fecha de fundación
    },
    "additionalProperties": True   # Se permiten otros campos extra no definidos
}
