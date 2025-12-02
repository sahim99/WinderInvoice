import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import User, Shop, UserRole
from app.auth import get_password_hash

def ensure_user():
    db = SessionLocal()
    try:
        # Ensure shop exists
        shop = db.query(Shop).first()
        if not shop:
            shop = Shop(name="Ambition Furniture", email="admin@ambition.com")
            db.add(shop)
            db.commit()
            db.refresh(shop)

        # Check/Create admin@example.com
        email = "admin@example.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                hashed_password=get_password_hash("admin123"),
                name="Example Admin",
                role=UserRole.ADMIN,
                shop_id=shop.id
            )
            db.add(user)
            db.commit()
            print(f"Created user {email}")
        else:
            # Update password to be sure
            user.hashed_password = get_password_hash("admin123")
            db.commit()
            print(f"User {email} exists. Password reset to admin123")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ensure_user()
