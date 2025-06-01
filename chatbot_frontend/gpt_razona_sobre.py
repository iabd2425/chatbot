import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

def gpt_razona_sobre(documentos, pregunta):
    if not OPENAI_API_KEY:
        return "⚠️ Faltan las credenciales de OpenRouter."

    hoteles_filtrados = documentos

    print("🚨 HOTELS FILTRADOS PARA GPT:")
    for h in hoteles_filtrados:
        print("-", h.get("nombre", "Sin nombre"), ">>>", h.get("localidad", "Ubicación desconocida"))

    def extraer_precio(precio_str):
        try:
            return float(str(precio_str).replace("€", "").replace(",", "").strip())
        except:
            return float("inf")

    hoteles_ordenados = sorted(hoteles_filtrados, key=lambda h: extraer_precio(h.get("precio", "")))

    contexto = ""
    for hotel in hoteles_ordenados[:5]:
        nombre = hotel.get("nombre", "Sin nombre")
        ubicacion = hotel.get("localidad", "Ubicación desconocida")
        descripcion = hotel.get("descripcion", "")
        servicios = ", ".join(hotel.get("servicios", []))
        precio = hotel.get("precio", "No disponible")
        puntuacion = hotel.get("puntuacion", "N/A")

        contexto += f"- {nombre} en {ubicacion}\n"
        contexto += f"  {descripcion}\n"
        contexto += f"  Servicios: {servicios}\n"
        contexto += f"  Precio: {precio} | Puntuación: {puntuacion}\n\n"

    prompt = (
        "Eres un experto en hoteles. Responde con precisión basándote en la lista que te doy. "
        "Devuelve el hotel más económico en Almería (ciudad), con su nombre, ubicación, precio y servicios principales.\n\n"
        f"### Datos de hoteles:\n{contexto}\n"
        f"### Pregunta del usuario:\n{pregunta}\n"
        "### Respuesta:"
    )

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        r = requests.post(f"{OPENAI_BASE_URL}/chat/completions", json=payload, headers=headers)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            return f"❌ Error GPT: {r.status_code} - {r.text}"
    except Exception as e:
        return f"🚨 Error al conectar con GPT: {e}"