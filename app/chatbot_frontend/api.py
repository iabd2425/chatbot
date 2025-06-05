import requests
import os
from dotenv import load_dotenv
from jose import jwt
from config import API_URL, API_VERSION

API_PREFIX = f"{API_URL}/{API_VERSION}"

def login_user(username, password):    
    response = requests.post(f"{API_PREFIX}/login", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()
    return None

def get_users(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_PREFIX}/users", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def create_user(username, password, is_admin, token):
    try:
        response = requests.post(f"{API_PREFIX}/register", json={
            "username": username,
            "password": password,
            "is_admin": is_admin
        }, headers={"Authorization": f"Bearer {token}"})
        return "✅ Usuario creado" if response.status_code == 200 else "❌ Error creando"
    except Exception as e:
        return f"⚠️ Error: {e}"

def update_user(user_id, username, password, is_admin, token):
    payload = {"username": username, "is_admin": is_admin}
    if password:
        payload["password"] = password
    try:
        r = requests.put(f"{API_PREFIX}/users/{user_id}", json=payload, headers={"Authorization": f"Bearer {token}"})
        return "✅ Usuario actualizado" if r.status_code == 200 else "❌ Error"
    except Exception as e:
        return f"⚠️ Error: {e}"

def delete_user(user_id, token):
    try:
        r = requests.delete(f"{API_PREFIX}/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
        return "✅ Usuario eliminado" if r.status_code == 200 else "❌ No se pudo eliminar"
    except:
        return "⚠️ Error al eliminar"

def chat_with_bot(message, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_PREFIX}/chat", headers=headers, json={"pregunta": message})
    if response.status_code == 200:
        return response.json()
    return None