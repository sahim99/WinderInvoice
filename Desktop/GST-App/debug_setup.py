from app.database import SessionLocal, engine, Base
from app import models
from app.services import auth_service
import sys

try:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    print("Checking shop...")
    shop = db.query(models.Shop).first()
    if not shop:
        print("Creating shop...")
        shop = models.Shop(
            name="My Furniture Shop",
            gstin="19AAAPJ2698R1ZO",
            address="123, Furniture Market",
            city="Kolkata",
            state="West Bengal",
            state_code="19",
            pincode="700001",
            phone="9876543210",
            email="shop@example.com"
        )
        db.add(shop)
        db.commit()
        db.refresh(shop)
    
    print("Checking user...")
    user = db.query(models.User).filter(models.User.email == "admin@example.com").first()
    if not user:
        print("Hashing password...")
        hashed_password = auth_service.get_password_hash("admin123")
        print(f"Password hashed: {hashed_password[:10]}...")
        
        user = models.User(
            shop_id=shop.id,
            name="Admin User",
            email="admin@example.com",
            hashed_password=hashed_password,
            role=models.UserRole.ADMIN
        )
        db.add(user)
        db.commit()
        print("User created.")
    else:
        print("User already exists.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
