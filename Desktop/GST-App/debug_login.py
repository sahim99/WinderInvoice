from app.database import SessionLocal
from app import models
from app.services import auth_service
import sys

try:
    db = SessionLocal()
    email = "admin@example.com"
    password = "admin123"
    
    print(f"Attempting login for {email}...")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        print("User not found!")
    else:
        print(f"User found: {user.email}")
        print(f"Stored hash: {user.hashed_password}")
        
        print("Verifying password...")
        try:
            is_valid = auth_service.verify_password(password, user.hashed_password)
            print(f"Password valid: {is_valid}")
        except Exception as e:
            print(f"Error verifying password: {e}")
            import traceback
            traceback.print_exc()

except Exception as e:
    print(f"Database error: {e}")
finally:
    db.close()
