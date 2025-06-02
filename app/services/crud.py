from sqlalchemy.orm import Session
from app import schemas
from app.models import models
from app.services.auth import hash_password, verify_password

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate, is_admin=False):
    hashed = hash_password(user.password)
    db_user = models.User(username=user.username, password=hashed, is_admin=is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(models.User).all()

def update_user(db: Session, user_id: int, updated_user: schemas.UserUpdate):
    user = get_user(db, user_id)
    if not user:
        return None
    user.username = updated_user.username
    if updated_user.password:
        user.password = hash_password(updated_user.password)
    user.is_admin = updated_user.is_admin
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user
