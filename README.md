# Chatbot de Hoteles Andaluces

Este proyecto implementa un **chatbot inteligente** para consultar información sobre hoteles en Andalucía. Combina un API REST con FastAPI, un motor de búsqueda en Elasticsearch, y modelos de lenguaje (OpenRouter u Ollama). Además, ofrece una interfaz web interactiva con Gradio y un panel de administración de usuarios.

---

## 📑 Tabla de Contenidos

1. [Características](#características)  
2. [Arquitectura y Flujo de Datos](#arquitectura-y-flujo-de-datos)  
3. [Estructura del Proyecto](#estructura-del-proyecto)  
4. [Requisitos Previos](#requisitos-previos)  
5. [Instalación y Configuración](#instalación-y-configuración)  
6. [Ejecución](#ejecución)  
7. [API REST](#api-rest)  
8. [Frontend con Gradio](#frontend-con-gradio)  
9. [Gestión de Usuarios](#gestión-de-usuarios)  
10. [Testing](#testing)  
11. [Variables de Entorno](#variables-de-entorno)  
12. [Contribuir](#contribuir)  
13. [Licencia](#licencia)  

---

## 🔥 Características

- Búsqueda de hoteles en lenguaje natural.  
- Integración con **Elasticsearch** para consultas avanzadas.  
- Soporte de **LLMs** a través de OpenRouter (API) o Ollama (local).  
- **Autenticación JWT**: registro, login, roles (admin/usuario).  
- **Interfaz web** con Gradio: chat, panel de administración, resultados enriquecidos.  
- Configuración flexible mediante archivo `.env`.  
- Logs rotativos y almacenamiento de conversaciones (opcional).  

---

## 🏗 Arquitectura y Flujo de Datos

1. El cliente (Gradio o cliente HTTP) envía una petición al endpoint `/v1/chat`.  
2. FastAPI valida el token JWT y extrae parámetros.  
3. Se consulta Elasticsearch para recuperar documentos relevantes.  
4. Se construye el prompt (historial + resultados) y se envía al LLM (OpenRouter u Ollama).  
5. La respuesta del LLM se retorna al cliente.  

Diagram:  
```
Cliente → FastAPI → Elasticsearch  
                        ↓  
                    LLM (OpenRouter/Ollama)  
                        ↓  
                   FastAPI → Cliente  
```

---

## 📂 Estructura del Proyecto

```
chatbot/
├── app/
│   ├── config.py            # Lectura de .env y settings
│   ├── database.py          # Conexión y modelo ORM
│   ├── main.py              # Punto de arranque FastAPI
│   ├── schemas.py           # Pydantic models
│   ├── models/              # Definición de tablas (SQLAlchemy)
│   ├── routers/             # Endpoints agrupados
│   ├── services/            # Lógica de negocio (Elasticsearch, LLM)
│   └── frontend/
│       └── frontend.py      # Interfaz Gradio
├── test/                    # Pruebas unitarias e integración
│   ├── test_api.py
│   └── test_elastic.py
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias Python
├── run_all.py               # Arranca backend + frontend juntos
├── create_admin.py          # Script para crear usuario admin
├── list_users.py            # Lista usuarios registrados
└── README.md                # Documentación del proyecto
```

---

## 🔧 Requisitos Previos

- Python 3.10+  
- Elasticsearch 8.x (local o en la nube)  
- Ollama (opcional, para LLM local)  
- OpenRouter API Key (si usa OpenRouter)  

---

## ⚙️ Instalación y Configuración

1. Clonar el repositorio y entrar en la carpeta:
   ```bash
   git clone <repo_url>
   cd proyectoIABD/chatbot/chatbot
   ```
2. Crear y configurar `.env` (ver [Variables de Entorno](#variables-de-entorno)).  
3. Crear un entorno virtual e instalar dependencias:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Inicializar la base de datos y crear usuario admin:
   ```bash
   python create_admin.py --username admin --password tu_pass
   ```

---

## ▶️ Ejecución

### Iniciar solo el Backend (FastAPI + Elasticsearch + LLM)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Iniciar el Frontend (Gradio)
```bash
python app/frontend/frontend.py
```
Visitar http://localhost:7860

### Todo en un solo comando
```bash
python run_all.py
```

---

## 📡 API REST

La documentación Swagger está disponible en http://localhost:8000/docs

### Endpoints Principales

- **POST** `/v1/register`  
  Registro de nuevo usuario.  
  Body: `{ "username": "user", "password": "pass" }`

- **POST** `/v1/login`  
  Obtención de JWT.  
  Body: `{ "username": "user", "password": "pass" }`  
  Respuesta: `{ "access_token": "token", "token_type": "bearer" }`

- **GET/POST/PUT/DELETE** `/v1/users`  
  Gestión de usuarios (solo **admin**).  

- **POST** `/v1/chat`  
  Consulta al chatbot.  
  Header: `Authorization: Bearer <token>`  
  Body: `{ "message": "¿Hoteles en Sevilla?" }`  
  Respuesta: `{ "response": "Aquí tienes..." }`

---

## 💻 Frontend con Gradio

- **Login**: introduce usuario y contraseña.  
- **Chat**: ventana de conversación, historial.  
- **Panel Admin**: lista, edita o elimina usuarios (solo rol admin).  

---

## 🛠 Testing

Ejecuta todas las pruebas con:
```bash
pytest --maxfail=1 --disable-warnings -q
```
- `test/test_api.py` – Pruebas de endpoints FastAPI.  
- `test/test_elastic.py` – Pruebas de consultas a Elasticsearch.  

---

## 📝 Variables de Entorno

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

1. Fork del repositorio.  
2. Crea una rama de feature: `git checkout -b feature/nueva-funcionalidad`.  
3. Realiza tus cambios y tests.  
4. Haz un PR detallado describiendo tu aporte.  

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Lee el archivo `LICENSE` para más detalles.  

## Autores
Rama "main" Antonio Domene Pérez
Rama "llm_backend-integration" Juan Carlos Camacho Sánchez
Curso de Especialización de IA y Big Data. I.E.S. Al Ándalus