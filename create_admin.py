from app.database import SessionLocal
from app import schemas
from app.services import crud

# Crear conexión a la base de datos
db = SessionLocal()

# Define el nuevo usuario admin
admin_user = schemas.UserCreate(username="adminmaster", password="1234")

# Crea el usuario con is_admin=True
crud.create_user(db, admin_user, is_admin=True)

print("✅ Usuario admin 'adminmaster' creado con éxito.")
