from app.database import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).all()
print("--- USERS ---")
for u in users:
    print(f"Email: {u.email}, Name: {u.name}, Role: {u.role}")
print("-------------")
db.close()
