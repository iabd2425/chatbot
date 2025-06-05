import logging
from fastapi import APIRouter, Depends, HTTPException
from app.services.llm import llm_chat
from app.services.auth import oauth2_scheme, decode_token

v1_router = APIRouter()

logger = logging.getLogger("chatbot")

@v1_router.post("/chat")
async def chat_v1(data: dict, token: str = Depends(oauth2_scheme)):
    """
    Manda pregunta al llm backend y devuelve su respuesta.
    """
    try:       
        payload = decode_token(token)
        username = payload.get("sub")
        pregunta = data["pregunta"]
        if not pregunta:
            raise HTTPException(status_code=400, detail="Pregunta no puede estar vacía.")
        else:
            logger.info(f'Usuario "{username}" pregunta: "{pregunta}"')
            respuesta = llm_chat(pregunta)
            logger.info(f'Respuesta del LLM a "{username}" : "{' '.join(respuesta['respuesta'].split())}"')
        return respuesta
    except HTTPException as e:
        raise e