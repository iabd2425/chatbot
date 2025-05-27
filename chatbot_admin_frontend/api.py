import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def login_user(username, password):
    response = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_users(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/users", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []
