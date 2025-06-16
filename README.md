# Chatbot de Hoteles Andaluces

Este proyecto implementa un **chatbot inteligente** diseñado para proporcionar información sobre hoteles en Andalucía. Combina varias tecnologías y componentes para ofrecer una experiencia completa e interactiva. El chatbot permite a los usuarios realizar consultas en lenguaje natural, aprovechando la potencia de la búsqueda semántica y los modelos de lenguaje.

---

## 📑 Tabla de Contenidos

1.  [Características](#características)
2.  [Arquitectura y Flujo de Datos](#arquitectura-y-flujo-de-datos)
3.  [Estructura del Proyecto](#estructura-del-proyecto)
4.  [Requisitos Previos](#requisitos-previos)
5.  [Instalación y Configuración](#instalación-y-configuración)
6.  [Ejecución](#ejecución)
7.  [API REST](#api-rest)
8.  [Frontend con Gradio](#frontend-con-gradio)
9.  [Gestión de Usuarios](#gestión-de-usuarios)
10. [Testing](#testing)
11. [Variables de Entorno](#variables-de-entorno)
12. [Contribuir](#contribuir)
13. [Licencia](#licencia)

---

## 🔥 Características

-   **Búsqueda de hoteles en lenguaje natural:** Los usuarios pueden interactuar con el chatbot utilizando lenguaje natural para buscar hoteles, lo que facilita la obtención de información.
-   **Integración con Elasticsearch para consultas avanzadas:** Se utiliza Elasticsearch como motor de búsqueda para indexar y buscar información sobre hoteles. Esto permite realizar consultas complejas y obtener resultados relevantes de manera eficiente.
-   **Soporte de LLMs a través de OpenRouter (API) u Ollama (local):** El proyecto integra modelos de lenguaje (LLMs) para comprender las consultas de los usuarios y generar respuestas coherentes. Se puede utilizar OpenRouter (a través de una API) o Ollama (ejecutado localmente) para acceder a estos modelos.
-   **Autenticación JWT**: registro, login, roles (admin/usuario):** Se implementa un sistema de autenticación basado en JSON Web Tokens (JWT) para gestionar el acceso de los usuarios. Esto incluye registro de nuevos usuarios, inicio de sesión y asignación de roles (administrador y usuario).
-   **Interfaz web con Gradio: chat, panel de administración, resultados enriquecidos:** Se proporciona una interfaz web interactiva construida con Gradio. Esta interfaz incluye un chat para interactuar con el chatbot, un panel de administración para gestionar usuarios y visualizar resultados enriquecidos.
-   **Configuración flexible mediante archivo .env:** El proyecto utiliza un archivo `.env` para almacenar variables de entorno, lo que facilita la configuración y el despliegue en diferentes entornos.
-   **Logs rotativos y almacenamiento de conversaciones (opcional):** Se ofrece la opción de habilitar logs rotativos para registrar eventos y conversaciones, lo que facilita el seguimiento y la depuración.

---

## 🏗 Arquitectura y Flujo de Datos

La arquitectura del proyecto se basa en una combinación de componentes que trabajan en conjunto para procesar las consultas de los usuarios y proporcionar respuestas relevantes. El flujo de datos se describe a continuación:

1.  **El cliente (Gradio o cliente HTTP) envía una petición al endpoint `/v1/chat`:** El usuario interactúa con el chatbot a través de la interfaz Gradio o mediante una petición HTTP a la API REST.
2.  **FastAPI valida el token JWT y extrae parámetros:** La API REST, construida con FastAPI, recibe la petición y valida el token JWT para autenticar al usuario. Luego, extrae los parámetros relevantes de la petición.
3.  **Se construye el prompt para generar una consulta Elastic y se envía al LLM (OpenRouter u Ollama):** Se construye un prompt basado en la pregunta del usuario para que el LLM genere la consulta Elastic correspondiente.
4.  **Se consulta Elasticsearch para recuperar documentos relevantes:** Se realiza una consulta a Elasticsearch para buscar información sobre hoteles que coincida con la consulta del usuario.
5.  **Se construye el prompt (historial + resultados) y se envía al LLM (OpenRouter u Ollama):** Se construye un prompt que incluye el historial de la conversación y los resultados de la búsqueda en Elasticsearch. Este prompt se envía al modelo de lenguaje (LLM) para generar una respuesta.
6.  **La respuesta del LLM se retorna al cliente:** La respuesta generada por el LLM se envía de vuelta al cliente, ya sea a través de la interfaz Gradio o como respuesta a la petición HTTP.

**Diagrama:**

```
Cliente → FastAPI → LLM (OpenRouter/Ollama)  
                        ↓  
                    Elasticsearch  
                        ↓  
                    LLM (OpenRouter/Ollama)  
                        ↓  
                   FastAPI → Cliente  
```

---


## 📂 Estructura del Proyecto

El proyecto está organizado en una estructura de directorios que facilita la gestión y el desarrollo. A continuación, se describe la estructura del proyecto:

```
chatbot/
├── app/
│   ├── config.py            # Lectura de .env y settings: Este archivo se encarga de leer las variables de entorno del archivo .env y configurar la aplicación.
│   ├── database.py          # Conexión y modelo ORM: Define la conexión a la base de datos y los modelos de datos utilizando SQLAlchemy.
│   ├── main.py              # Punto de arranque FastAPI: Es el punto de entrada principal de la aplicación FastAPI, donde se definen las rutas y se inicializan los componentes.
│   ├── schemas.py           # Pydantic models: Define los modelos de datos utilizando Pydantic para la validación y serialización de datos.
│   ├── models/              # Definición de tablas (SQLAlchemy): Contiene las definiciones de las tablas de la base de datos utilizando SQLAlchemy.
│   ├── routers/             # Endpoints agrupados: Agrupa las rutas (endpoints) de la API REST por funcionalidad.
│   ├── services/            # Lógica de negocio (Elasticsearch, LLM): Contiene la lógica de negocio, como la interacción con Elasticsearch y los modelos de lenguaje.
│   └── frontend/
│       └── frontend.py      # Interfaz Gradio: Implementa la interfaz de usuario con Gradio.
├── test/                    # Pruebas unitarias e integración: Contiene las pruebas unitarias y de integración para asegurar la calidad del código.
│   ├── test_api.py
│   └── test_elastic.py
├── .env                     # Variables de entorno: Contiene las variables de entorno necesarias para la configuración de la aplicación.
├── requirements.txt         # Dependencias Python: Lista las dependencias de Python necesarias para ejecutar el proyecto.
├── run_all.py               # Arranca backend + frontend juntos: Script para iniciar el backend (FastAPI) y el frontend (Gradio) simultáneamente.
├── create_admin.py          # Script para crear usuario admin: Script para crear un usuario administrador en la base de datos.
├── list_users.py            # Lista usuarios registrados: Script para listar los usuarios registrados en la base de datos.
└── README.md                # Documentación del proyecto: Este archivo, que describe el proyecto.
```

---

## 🔧 Requisitos Previos

Para ejecutar este proyecto, se necesitan los siguientes requisitos previos:

-   **Python 3.10+:** Se requiere Python 3.10 o superior para ejecutar el código.
-   **Elasticsearch 8.x (local o en la nube):** Se necesita una instancia de Elasticsearch para almacenar y buscar información sobre hoteles.
-   **Ollama (opcional, para LLM local):** Si se desea utilizar un modelo de lenguaje localmente, se necesita Ollama.
-   **OpenRouter API Key (si usa OpenRouter):** Si se utiliza OpenRouter para acceder a los modelos de lenguaje, se necesita una clave de API.

---

## ⚙️ Instalación y Configuración

Sigue estos pasos para instalar y configurar el proyecto:

1.  **Clonar el repositorio y entrar en la carpeta:**

    ```bash
    git clone <repo_url>
    cd proyectoIABD/chatbot/chatbot
    ```
2.  **Crear y configurar .env (ver [Variables de Entorno](#variables-de-entorno)):** Crea un archivo `.env` en la raíz del proyecto y configura las variables de entorno necesarias.
3.  **Crear un entorno virtual e instalar dependencias:**

    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    pip install -r requirements.txt
    ```
4.  **Inicializar la base de datos y crear usuario admin:**

    ```bash
    python create_admin.py --username admin --password tu_pass
    ```

---

## ▶️ Ejecución

El proyecto se puede ejecutar de varias maneras:

### Iniciar solo el Backend (FastAPI + Elasticsearch + LLM)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Este comando inicia el backend de la aplicación, que incluye la API REST (FastAPI), la conexión a Elasticsearch y la integración con el modelo de lenguaje (LLM).

### Iniciar el Frontend (Gradio)

```bash
python app/frontend/frontend.py
```

Este comando inicia la interfaz de usuario construida con Gradio, que permite interactuar con el chatbot a través de un navegador web.

Visitar http://localhost:7860

### Todo en un solo comando

```bash
python run_all.py
```

Este comando ejecuta un script que inicia tanto el backend como el frontend simultáneamente.

---

## 📡 API REST

La API REST proporciona los endpoints necesarios para interactuar con el chatbot. La documentación Swagger está disponible en http://localhost:8000/docs

### Endpoints Principales

-   **POST** `/v1/register`
    Registro de nuevo usuario.
    Body: `{ "username": "user", "password": "pass" }`

-   **POST** `/v1/login`
    Obtención de JWT.
    Body: `{ "username": "user", "password": "pass" }`
    Respuesta: `{ "access_token": "token", "token_type": "bearer" }`

-   **GET/POST/PUT/DELETE** `/v1/users`
    Gestión de usuarios (solo **admin**).

-   **POST** `/v1/chat`
    Consulta al chatbot.
    Header: `Authorization: Bearer <token>`
    Body: `{ "message": "¿Hoteles en Sevilla?" }`
    Respuesta: `{ "response": "Aquí tienes..." }`

---

## 💻 Frontend con Gradio

La interfaz de usuario con Gradio ofrece las siguientes funcionalidades:

-   **Login**: Permite a los usuarios autenticarse con sus credenciales.
-   **Chat**: Proporciona una ventana de conversación donde los usuarios pueden interactuar con el chatbot y ver el historial de sus consultas.
-   **Panel Admin**: Permite a los administradores gestionar usuarios, incluyendo la lista, edición y eliminación de usuarios.

---

## 🛠 Testing

El proyecto incluye pruebas unitarias e integración para asegurar la calidad del código.

Ejecuta todas las pruebas con:

```bash
pytest --maxfail=1 --disable-warnings -q
```

-   `test/test_api.py` – Pruebas de endpoints FastAPI.
-   `test/test_elastic.py` – Pruebas de consultas a Elasticsearch.

---

## 📝 Variables de Entorno

Las variables de entorno se utilizan para configurar el proyecto y se almacenan en el archivo `.env`. A continuación, se muestra un ejemplo de las variables de entorno:

```env
# FastAPI & JWT
SECRET_KEY=frase_super_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme
ES_INDEX=hoteles

# OpenRouter
USE_OPEN_ROUTER=true
OPENROUTER_API_KEY=tu_api_key
OPENROUTER_API_BASE=https://api.openrouter.ai
OPENROUTER_MODEL=llama3.2:3b

# Ollama (si USE_OPEN_ROUTER=false)
OLLAMA_MODEL=llama3.2:3b

# Base de datos
DATABASE_URL=sqlite:///./app.db

# Logs
LOG_DIRECTORY=./logs
```

---

## 🤝 Contribuir

Si deseas contribuir a este proyecto, sigue estos pasos:

1.  Fork del repositorio.
2.  Crea una rama de feature: `git checkout -b feature/nueva-funcionalidad`.
3.  Realiza tus cambios y tests.
4.  Haz un PR detallado describiendo tu aporte.

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Lee el archivo `LICENSE` para más detalles.

## Autores

Rama "main" Antonio Domene Pérez
Rama "llm_backend-integration" Juan Carlos Camacho Sánchez
Curso de Especialización de IA y Big Data. I.E.S. Al Ándalus