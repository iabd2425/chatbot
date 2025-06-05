import logging
from logging.handlers import TimedRotatingFileHandler
import os
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()

# Elasticsearch
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST')
ELASTICSEARCH_PORT = os.getenv('ELASTICSEARCH_PORT')
ELASTICSEARCH_USERNAME = os.getenv('ELASTICSEARCH_USERNAME')
ELASTICSEARCH_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD')
ES_INDEX = os.getenv('ES_INDEX')

# OpenRouter
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_API_BASE = os.getenv('OPENROUTER_API_BASE')
OPENROUTER_SITE_URL = os.getenv('OPENROUTER_SITE_URL')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL')

# Ollama
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')

# Usar OpenRouter u Ollama
USE_OPEN_ROUTER = os.getenv("USE_OPEN_ROUTER", "false").lower() == "true"

# Directorio de salida
LOG_DIRECTORY = os.getenv('LOG_DIRECTORY', "./logs")

# Auth
SECRET_KEY = os.getenv("SECRET_KEY", "secret")

# Base de datos de usuarios
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

def config_logging():
    # Silenciar loggers de terceros
    for noisy_logger in [
        "uvicorn", "uvicorn.access", "uvicorn.error",
        "fastapi", "httpx", "urllib3", "requests", "ollama"
    ]:
        logging.getLogger(noisy_logger).propagate = False
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    # Ruta al fichero de log
    if not os.path.exists(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)

    log_path = os.path.join(LOG_DIRECTORY, "chatbot.log")

    # Verificar permisos de escritura
    try:
        with open(log_path, 'a'):
            pass
    except IOError as e:
        print(f"Warning: No se puede escribir en {log_path}. Error: {e}")
        return

    # Crear logger personalizado
    logger = logging.getLogger("chatbot")
    logger.setLevel(logging.INFO)
    logger.propagate = False  # No propaga al root logger

    # Limpiar handlers existentes
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])

    # Handler rotativo diario
    handler = TimedRotatingFileHandler(
        log_path, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    handler.suffix = "_%Y%m%d"
    formatter = logging.Formatter('%(asctime)s - CHATBOT - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)