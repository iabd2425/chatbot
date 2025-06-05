from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import logging
from app.database import SessionLocal
from app import schemas
from app.models import models
from app.services import auth, crud

v1_router = APIRouter()

logger = logging.getLogger("chatbot")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@v1_router.post("/register", response_model=schemas.UserOut)
def register_v1(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    logger.info(f"Registro usuario: {user.username}")
    return crud.create_user(db, user, is_admin=user.is_admin)  # ✅ Añadir esto


@v1_router.post("/login")
def login_v1(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    # 👇 Añadimos is_admin dentro del token
    access_token = auth.create_access_token(data={
        "sub": user.username,
        "is_admin": user.is_admin
    })
    logger.info(f"Login usuario: {user.username}")
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

