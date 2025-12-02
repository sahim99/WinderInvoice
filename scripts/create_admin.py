import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import User, Shop, UserRole
from app.auth import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        # Ensure shop exists
        shop = db.query(Shop).first()
        if not shop:
            shop = Shop(name="Ambition Furniture", email="admin@ambition.com")
            db.add(shop)
            db.commit()
            db.refresh(shop)
            print("Created default shop.")

        # Check if admin exists
        user = db.query(User).filter(User.email == "admin@ambition.com").first()
        if not user:
            user = User(
                email="admin@ambition.com",
                hashed_password=get_password_hash("admin"),
                name="Admin User",
                role=UserRole.ADMIN,
                shop_id=shop.id
            )
            db.add(user)
            db.commit()
            print("Admin user created successfully.")
        else:
            # Reset password just in case
            user.hashed_password = get_password_hash("admin")
            db.commit()
            print("Admin user exists. Password reset to 'admin'.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
