import os
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()

load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_VERSION = os.getenv("API_VERSION", "v1")

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
