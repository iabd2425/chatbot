ELASTIC_INTRO_PROMPT= """
Eres un experto en Elasticsearch. Dado el siguiente esquema de indice de hoteles, genera SOLO la consulta JSON valida para buscar detalles del hotel solicitado. No expliques nada ni pregunges, solo genera la consulta.

Esquema:
- nombre: text
- marca: text
- provincia: text
- localidad: text
- direccion: text
- servicios: text
- location: geo_point
- descripcion: text
- destacados: text
- opinion: float
- comentarios: integer
- precio: integer
- fechaEntrada: date (yyyy-MM-dd)

"""

FEW_SHOT_PROMPT = """
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
Pregunta: "Dime hoteles que en Málaga disponibles el 10 de julio de 2025."
Respuesta JSON:
{
  "query": {
    "bool": {
      "filter": [
        { "match": { "localidad": "Málaga" } },
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
Pregunta: "¿Cual es el hotel La Perla?"
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
Pregunta: "Búscame hoteles de Huelva ordenados por precio descendente."
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
Pregunta: "Búscame hoteles de Huelva ordenados por precio descendente."
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
Pregunta: "¿Cual es el hotel mas barato de la provincia de Cádiz?"
Pregunta: "Búscame hoteles de Cádiz ordenados por precio ascendente."
Respuesta JSON:
{
  "query": {
    "match": {
      "provincia": "Cádiz"
    }
  },
  "sort": [
    { "precio": "asc" }
  ],
  "size": 1
}

Ejemplo 7:
Pregunta: Recomiendame dos hoteles de la ciudad de málaga
Respuesta JSON:
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

Ejemplo 8:
Pregunta: "Búscame hoteles de la marca o grupo o cadena Senator de la provincia de Almería"
Respuesta JSON:
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "marca": "Senator"
          }
        },
        {
          "match": {
            "provincia": "Almería"
          }
        }
      ]
    }
  },
  "collapse": {
    "field": "id"
  }
}

Ejemplo 9:
Pregunta: "Dime el hotel que tiene más comentarios de la provincia de Córdoba"
Respuesta JSON:
{
  "query": {
    "match": {
      "provincia": "Córdoba"
    }
  },
  "sort": [
    { "comentarios": "desc" }
  ],
  "collapse": {
    "field": "id"
  },
  "size": 1
}

Ejemplo 10:
Pregunta: "¿Cual es el hotel con mejor opinión, puntuación o nota de la provincia de Sevilla?"
Pregunta: "¿Cual es el hotel mejor valorado de la provincia de Sevilla?"
Respuesta JSON:
{
  "query": {
    "match": {
      "provincia": "Sevila"
    }
  },
  "sort": [
    { "opinion": "desc" }
  ],
  "collapse": {
    "field": "id"
  },
  "size": 1
}  

Ejemplo 11:
Pregunta: "Busca un hotel en Huelva de la marca o grupo Senator"
Respuesta JSON:
{
  "query": {
    "bool": {
      "must": [
        { "match": { "marca": "Senator" } },
        { "match": { "provincia": "Huelva" } }
      ]
    }
  },
  "size": 1
}

"""

ELASTIC_END_PROMPT = """
Ahora, genera SOLO la consulta JSON para esta pregunta:
"{pregunta}"
"""

ELASTIC_PROMPT = ELASTIC_INTRO_PROMPT + FEW_SHOT_PROMPT + ELASTIC_END_PROMPT