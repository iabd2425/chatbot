import os
import json
import re
from uuid import uuid4
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv

load_dotenv()

ES_API_KEY = os.getenv("ES_API_KEY")
ES_HOST = os.getenv("ES_HOST")
ES_INDEX = os.getenv("ES_INDEX", "hoteles")

# Conexión a Elasticsearch (usa api_key o basic_auth según tu config)
es = Elasticsearch(
    hosts=[ES_HOST],
    api_key=ES_API_KEY,
    verify_certs=False
)

# Utilidades de conversión
def clean_float(val):
    if isinstance(val, str):
        val = val.replace(",", ".").strip()
    try:
        return float(val)
    except:
        return 0.0

def clean_int(val):
    try:
        return int(re.search(r"\d+", str(val)).group())
    except:
        return 0

def parse_coords(coord_str):
    try:
        lat, lon = map(float, coord_str.split(","))
        return {"lat": lat, "lon": lon}
    except:
        return None

def normalize_boolean(value):
    if isinstance(value, str):
        v = value.strip().lower()
        return v in ["sí", "si", "permitidas", "true"]
    return bool(value)

def index_hotels_from_json(json_path):
    """Carga e indexa datos normalizados desde un archivo JSON."""
    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    actions = []
    for h in raw_data:
        doc = {
            "id": h.get("ID Hotel", ""),
            "nombre": h.get("Nombre", ""),
            "marca": h.get("Marca", "N/A"),
            "localidad": h.get("Dirección", ""),
            "descripcion": h.get("Descripción", ""),
            "servicios": h.get("Servicios populares", []),
            "mascotas": normalize_boolean(h.get("¿Mascotas?", "no disponible")),
            "coordenadas": parse_coords(h.get("Coordenadas", "")),
            "opinion": clean_float(h.get("Opinión", 0)),
            "comentarios": clean_int(h.get("Numero comentarios", 0)),
            "url": h.get("URL hotel", ""),
            "precio": clean_int(h.get("Precio", 0)),
            "fechaEntrada": h.get("Fecha entrada", ""),
            "fechaSalida": h.get("Fecha salida", ""),
            "destacados": h.get("destacados", "N/A")
        }

        # ID único por documento
        doc_id = f"{doc['id']}_{doc['fechaEntrada']}_{uuid4()}"

        actions.append({
            "_index": ES_INDEX,
            "_id": doc_id,
            "_source": doc
        })

    helpers.bulk(es, actions)
    print(f"✅ Indexados {len(actions)} documentos en '{ES_INDEX}'.")

def query_elasticsearch(question, size=3):
    """Realiza una búsqueda por texto libre con tolerancia a errores."""
    response = es.search(
        index=ES_INDEX,
        size=size,
        query={
            "multi_match": {
                "query": question,
                "fields": [
                    "nombre^3",
                    "descripcion^2",
                    "localidad",
                    "servicios"
                ],
                "fuzziness": "AUTO"
            }
        }
    )

    hits = response["hits"]["hits"]
    if not hits:
        return "❌ No se encontraron coincidencias."

    result = "🏨 Resultados:\n"
    for h in hits:
        src = h["_source"]
        result += f"- **{src.get('nombre', 'Hotel sin nombre')}** en {src.get('localidad', 'ubicación desconocida')}\n"
        result += f"  {src.get('descripcion', '')}\n"
        result += f"  Servicios: {', '.join(src.get('servicios', []))}\n"
        result += f"  Precio: {src.get('precio', 'No disponible')}€\n"
        result += f"  URL: {src.get('url', 'No disponible')}\n\n"

    return result.strip()

def query_elasticsearch_raw(question, size=3):
    """Devuelve los documentos completos como lista de diccionarios."""
    try:
        response = es.search(
            index=ES_INDEX,
            size=size,
            query={
                "multi_match": {
                    "query": question,
                    "fields": [
                        "nombre^3",
                        "descripcion^2",
                        "localidad",
                        "servicios"
                    ],
                    "fuzziness": "AUTO"
                }
            }
        )
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        print("❌ Error en query_elasticsearch_raw:", e)
        return []

if __name__ == "__main__":
    index_hotels_from_json("hoteles.json")
    print("\n🔎 Consulta de prueba:")
    print(query_elasticsearch("playa piscina almería"))

    # Verifica si hay datos y muestra uno
    res = es.search(index=ES_INDEX, size=1)
    if res["hits"]["hits"]:
        print("\n📄 Documento real indexado:")
        print(json.dumps(res["hits"]["hits"][0]["_source"], indent=2))
    else:
        print("\n⚠️ No se encontraron documentos en el índice", ES_INDEX)
