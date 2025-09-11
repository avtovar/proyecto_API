import os

import  requests
from jsonschema import validate

BASE_URL = os.getenv("BASE_URL")
USERS = "/users/"

user_schema = {
    "type": "object",
    "required": ["id", "email", "full_name", "role"],
    "properties": {
        "id": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "full_name": {"type": "string"},
        "role": {"type": "string", "enum": ["passenger", "admin"]}
    },
    "additionalProperties": True
}

def test_create_user_schema(user):
    validate(instance=user, schema=user_schema)


def test_get_all_users(auth_headers, limit=10):
    skip = 0
    results = []

    while True:
        r = requests.get(f"{BASE_URL}{USERS}", params={"skip": skip, "limit": limit})
        r.raise_for_status()
        users_list = r.json()

        if not users_list:
            break
        results.extend(users_list)
        skip += limit

    return results