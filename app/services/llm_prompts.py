FEW_SHOT_PROMPT = """
Eres un experto en Elasticsearch. Dado el siguiente esquema de indice de hoteles, genera SOLO la consulta JSON valida para buscar detalles del hotel solicitado. No expliques nada ni pregunges, solo genera la consulta.

Esquema:
- nombre: text
- provincia: text
- localidad: text
- servicios: text
- location: geo_point
- descripcion: text
- precio: integer
- fechaEntrada: date (yyyy-MM-dd)

Ejemplo 1:
Pregunta: "Muustrame hoteles en Aguadulce con piscina y parking, ordenados por precio ascendente para el dia 01/06/2025."
Respuesta JSON:
{
  "query": {
    "bool": {
      "must": [
        { "match": { "localidad": "aguadulce" } },
        { "term": { "fechaEntrada":  "2025-06-01"  } },
        {
          "bool": {
            "should": [
              { "match": { "servicios": "piscina" } },
              { "match": { "servicios": "parking" } }
            ],
            "minimum_should_match": 2
          }
        }
      ]
    }
  },
  "sort": [
    { "precio": "asc" }
  ],
  "size": 10
}

Ejemplo 2:
Pregunta: "Dime hoteles que en Madrid disponibles el 10 de julio de 2025."
Respuesta JSON:
{
  "query": {
    "bool": {
      "filter": [
        { "match": { "localidad": "Madrid" } },
        { "term": { "fechaEntrada": "2025-07-10" } }
      ]
    }
  },
  "collapse": {
    "field": "id"
  },
  "size": 10
}

Ejemplo 3:
Pregunta: "Quiero conocer los detalles del hotel La Perla."
Respuesta JSON:
{
  "query": {
    "match": {
      "nombre": "La Perla"
    }
  },
  "size": 1
}

Ejemplo 4:
Pregunta: "¿Cual es el hotel mas barato de la provincia de Huelva?"
Respuesta JSON:
{
  "query": {
    "match": {
      "provincia": "Huelva"
    }
  },
  "sort": [
    { "precio": "asc" }
  ],
  "size": 1
}

Ejemplo 5:
Pregunta: "¿Cual es el hotel mas caro de Huelva?"
Respuesta JSON:
{
  "query": {
    "match": {
      "localidad": "Huelva"
    }
  },
  "sort": [
    { "precio": "desc" }
  ],
  "size": 1
}

Ejemplo 6:
Pregunta: Recomiendame dos hoteles de la ciudad de málaga
{
  "query": {
    "match": {
      "localidad": "Málaga"
    }
  },
  "collapse": {
    "field": "id"
  },
  "size": 2
}


Ahora, genera SOLO la consulta JSON para esta pregunta:
"{pregunta}"
"""