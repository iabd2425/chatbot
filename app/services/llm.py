import time
from datetime import datetime
from functools import wraps
import logging
import json
import re
from elasticsearch import Elasticsearch
from app.config import (ELASTICSEARCH_HOST, ELASTICSEARCH_PORT, ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD, ES_INDEX, 
                        OPENROUTER_API_KEY, OPENROUTER_API_BASE, OPENROUTER_SITE_URL, OPENROUTER_MODEL, 
                        USE_OPEN_ROUTER, OLLAMA_MODEL)

from app.services.llm_prompts import ELASTIC_PROMPT

logger = logging.getLogger("chatbot")

if USE_OPEN_ROUTER:
    from openai import OpenAI
    
    openai_client = OpenAI(
        base_url=OPENROUTER_API_BASE,
        api_key=OPENROUTER_API_KEY,
        default_headers={"HTTP-Referer": OPENROUTER_SITE_URL}
    )
else:
    import ollama
    import requests

# Elasticsearch connection
es = Elasticsearch(
    [f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"],
    basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
)

def medir_tiempo(nombre_funcion: str = None):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            inicio = time.perf_counter()
            resultado = func(*args, **kwargs)
            fin = time.perf_counter()
            duracion = fin - inicio
            minutos = int(duracion // 60)
            segundos = duracion % 60
            nombre = nombre_funcion or func.__name__
            if minutos > 0:
                logger.info(f"{nombre} tardó {minutos} minutos y {segundos:.2f} segundos.")
            else:
                logger.info(f"{nombre} tardó {duracion:.2f} segundos.")
            return resultado
        return wrapper
    return decorador


def extraer_json_valido(texto):
    try:
        match = re.search(r'\{.*\}', texto, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            error_msg = "No se encontró un bloque JSON válido."
            logger.info(error_msg)
            raise ValueError(error_msg)
    except json.JSONDecodeError as e:
        print("Error al parsear JSON:", e)
        print("Respuesta raw:\n", texto)
        return None

@medir_tiempo("Generar Query desde LLM")
def generar_consulta_llm(pregunta: str) -> dict:    
    prompt = ELASTIC_PROMPT.replace("{pregunta}", pregunta)

    if USE_OPEN_ROUTER:
        try:
            respuesta = openai_client.chat.completions.create(
                        model=OPENROUTER_MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        timeout=60
                    )            
            contenido = respuesta.choices[0].message.content
            return contenido
        except Exception as e:
            error_msg = "Error al llamar a OpenRouter: " + str(e)
            logger.error(error_msg)
            print(error_msg)
            return "Error OpenRouter"
    else:
        try:
            respuesta = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1},
            )
            contenido = respuesta["message"]["content"]
            return contenido            
        except requests.exceptions.RequestException as e:
            error_msg = "Error al llamar a Ollama: " + str(e)
            logger.error(error_msg)
            print(error_msg)
            return None


def procesar_consulta_generada(contenido: str) -> dict:
    try:
        consulta = extraer_json_valido(contenido)
        if not consulta:
            error_msg = "Consulta generada no contiene un JSON válido."
            logger.error(error_msg)
            raise ValueError(error_msg)
        json_comprimido = json.dumps(consulta, separators=(',', ':'))
        logger.info(f"Consulta generada: {json_comprimido}")
        return json_comprimido
    except ValueError as e:
        error_msg = f"Error al procesar la consulta generada: {e}"
        logger.error(error_msg)
        print(error_msg)
        return None

@medir_tiempo("Consulta a Elasticsearch")    
def buscar_en_elasticsearch(consulta: dict):
    return es.search(index=ES_INDEX, body=consulta)

def obtener_num_resultados(resultados) -> int:
    if resultados and "hits" in resultados:
        return len(resultados.get("hits", {}).get("hits", []))
    return 0

def recortar_url(url: str) -> str:
    match = re.match(r"(https://www\.booking\.com/hotel/.+?\.html)", url)
    return match.group(1) if match else url

def obtener_dataset_hoteles(resultados) -> list:
    hits = resultados.get("hits", {}).get("hits", [])
    dataset = []
    for hit in hits:
        hotel = hit["_source"]
        servicios = hotel.get("servicios", [])
        hotel_data = {
            "nombre": hotel.get('nombre', 'N/A'),
            "url": recortar_url(hotel.get('url', 'N/A')),
            "coordenadas": hotel.get('location', 'N/A')
        }
        dataset.append(hotel_data)
    return dataset

def construir_prompt_multiple(pregunta, resultados) -> str:
    hits = resultados.get("hits", {}).get("hits", [])
    if not hits:
        return "No se encontraron resultados."

    prompt = f"A la pregunta: '{pregunta}' se han encontrado {len(hits)} hoteles. "
    prompt += "Describe brevemente y en lenguaje natural los siguientes hoteles encontrados:\n\n"
    for hit in hits:
        hotel = hit["_source"]
        servicios = hotel.get("servicios", [])
        prompt += f"""Hotel {hotel.get('nombre', 'N/A')}:

- Provincia: {hotel.get('provincia', 'N/A')}
- Localidad: {hotel.get('localidad', 'N/A')} 
- Direccion: {hotel.get('direccion', 'N/A')}
- Descripcion: {hotel.get('descripcion', '')}
- Servicios: {', '.join(servicios) if isinstance(servicios, list) else servicios}
- Puntuacion: {hotel.get('opinion', 'Sin opiniones')} 
- Número de comentarios: ({hotel.get('comentarios', '0')} comentarios)
- Precio: {hotel.get('precio', 'N/A')} EUR
"""
    return prompt.strip()

@medir_tiempo("Respuesta final del LLM")
def respuesta_natural(texto_prompt: str, dataset_hoteles: list) -> str:
    if USE_OPEN_ROUTER:
        try:
            respuesta = openai_client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[{"role": "user", "content": texto_prompt}],
                timeout=60
            )
            mensaje = respuesta.choices[0].message.content
            return mensaje
        except Exception as e:
            error_msg = "Error al llamar a OpenRouter: " + str(e)
            logger.error(error_msg)
            print(error_msg)
            return "Error OpenRouter"
    else:
        try:
            respuesta = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": texto_prompt}],
                options={"temperature": 0.1}
            )
            return respuesta["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            error_msg = "Error al llamar a Ollama: " + str(e)
            logger.error(error_msg)
            print(error_msg)
            return None

def main():
    pregunta_usuario = input("Pregunta sobre hoteles: ")
    logger.info(f"Pregunta: {pregunta_usuario}")
    consulta = generar_consulta_llm(pregunta_usuario)
    consulta = procesar_consulta_generada(consulta)
    if not consulta:
        return {"respuesta": "No se pudo generar una consulta válida.", "hits": 0, "resultados": []}
    resultados = buscar_en_elasticsearch(consulta)
    prompt_hoteles = construir_prompt_multiple(resultados)
    respuesta = respuesta_natural(prompt_hoteles)
    print("\nRespuesta:\n", respuesta)
    logger.info("Respuesta: " + respuesta)

def llm_chat(pregunta : str) -> dict:
    consulta = generar_consulta_llm(pregunta)
    if consulta == "Error OpenRouter":
        return {"respuesta": "Límite diario de uso de OpenRouter. Cambiar a local.", "hits": 0, "resultados": []}
    consulta = procesar_consulta_generada(consulta)
    if not consulta:
        return {"respuesta": "No se pudo generar una consulta válida.", "hits": 0, "resultados": []}
    resultados = buscar_en_elasticsearch(consulta)
    hit_count = obtener_num_resultados(resultados)
    dataset_hoteles = obtener_dataset_hoteles(resultados)    
    prompt_hoteles = construir_prompt_multiple(pregunta, resultados)
    respuesta = respuesta_natural(prompt_hoteles, dataset_hoteles)
    if respuesta == "Error OpenRouter":
        return {"respuesta": "Límite diario de uso de OpenRouter. Cambiar a local.", "hits": 0, "resultados": []}
    return {"respuesta": respuesta, "hits": hit_count, "resultados": dataset_hoteles}

if __name__ == "__main__":
    main()