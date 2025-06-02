from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False  # ✅ Añadir esto


class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: str
    password: Optional[str] = None
    is_admin: bool

    class Config:
        from_attributes = True  # si estás en Pydantic v2
