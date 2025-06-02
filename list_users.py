from app.database import SessionLocal
from app.models.models import User

db = SessionLocal()
users = db.query(User).all()

print("\nUsuarios registrados:\n")
for u in users:
    print(f"ID: {u.id} | Usuario: {u.username} | Admin: {u.is_admin}")
