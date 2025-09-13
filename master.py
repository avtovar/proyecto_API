import requests

URL = "https://cf-automation-airline-api.onrender.com"
AUTH_LOGIN = "/auth/login/"
AUTH_SIGNUP = "/users/"
LIST_USERS = "/users?skip=0&limit=10"


admin_data = {
    "username": "admin@demo.com",
    "password": "admin123"
}

support_user_data = {
    "email": "alondra.tovar@airline.com",
    "password": "Alon12345",
    "full_name": "Alondra Tovar",
    "role": "admin"
}


def login_as_admin():
    r = requests.post(URL + AUTH_LOGIN, data=admin_data)
    return r


def signup_support_user(support_data):
    r = requests.post(URL + AUTH_SIGNUP, json=support_data,
                      headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3ItMmIzM2M2YTEiLCJyb2xlIjoiYWRtaW4ifQ.rWFwFMLax1o_Qu8h5nMX8ePLZVDvluJZK63tT85XC1I"})
    return r

print(signup_support_user(support_user_data).json())