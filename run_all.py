import subprocess
import os

def run_backend():
    """Ejecuta el backend FastAPI con uvicorn."""
    try:
        subprocess.Popen(["uvicorn", "app.main:app", "--reload"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Backend FastAPI iniciado.")
    except Exception as e:
        print(f"Error iniciando backend: {e}")

def run_frontend():
    """Ejecuta el frontend Gradio."""
    try:
        subprocess.Popen(["python", "app/chatbot_frontend/main.py"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Frontend Gradio iniciado.")
    except Exception as e:
        print(f"Error iniciando frontend: {e}")

if __name__ == "__main__":
    run_backend()
    run_frontend()
    print("El backend y frontend están iniciándose.  Comprueba la salida del terminal para obtener sus respectivos urls.")