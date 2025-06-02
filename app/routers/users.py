from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.auth import oauth2_scheme, decode_token
from app.models.models import User
from app.schemas import UserOut
from app import schemas
from app.services import crud


v1_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@v1_router.get("/users", response_model=list[UserOut])
def list_users_v1(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(User).all()


@v1_router.put("/users/{user_id}", response_model=UserOut)
def update_user_v1(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.update_user(db, user_id, user)

@v1_router.delete("/users/{user_id}")
def delete_user_v1(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.delete_user(db, user_id)