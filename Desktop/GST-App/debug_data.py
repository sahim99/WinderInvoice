from app.database import SessionLocal
from app import models

db = SessionLocal()
customers = db.query(models.Customer).all()
print(f"Total Customers: {len(customers)}")
for c in customers:
    print(f"ID: {c.id}, Name: {c.name}, ShopID: {c.shop_id}")

products = db.query(models.Product).all()
print(f"Total Products: {len(products)}")
for p in products:
    print(f"ID: {p.id}, Name: {p.name}, ShopID: {p.shop_id}")

db.close()
