from fastapi import FastAPI
from app import config
from app.config import config_logging
from app.routers import auth, users, chat

config_logging()

app = FastAPI(
    title="Chatbot API",
    description="API para el chatbot",
    version="0.1.0",
)


@app.get("/")
async def read_root():
    return {"message": "Esta es la documentacion de la API del chatbot"}

app.include_router(auth.v1_router, prefix="/v1")
app.include_router(users.v1_router, prefix="/v1")
app.include_router(chat.v1_router, prefix="/v1")
