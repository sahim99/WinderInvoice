import sys
import os
from datetime import date, timedelta

# Add parent directory to path to import app modules
sys.path.append(os.getcwd())

from app.database import SessionLocal, engine, Base
from app.models import Shop, User, Customer, Product, Invoice, InvoiceItem, UserRole
from app.auth import get_password_hash

def create_test_data():
    db = SessionLocal()
    
    try:
        print("Creating test data...")
        
        # 1. Update Shop Settings
        shop = db.query(Shop).first()
        if not shop:
            shop = Shop(name="Ambition Furniture", email="admin@ambition.com")
            db.add(shop)
            db.commit()
            db.refresh(shop)
            
        shop.name = "Ambition Furniture"
        shop.address = "123, Furniture Market, Main Road"
        shop.city = "Mumbai"
        shop.state = "Maharashtra"
        shop.pincode = "400001"
        shop.phone = "9876543210"
        shop.email = "contact@ambitionfurniture.com"
        shop.gstin = "27ABCDE1234F1Z5"
        shop.bank_name = "HDFC Bank"
        shop.account_number = "123456789012"
        shop.ifsc_code = "HDFC0001234"
        db.commit()
        print("Shop settings updated.")

        # 2. Create Customer
        customer = db.query(Customer).filter(Customer.email == "rahul@example.com").first()
        if not customer:
            customer = Customer(
                shop_id=shop.id,
                name="Rahul Sharma",
                billing_address="Flat 101, Galaxy Apartments, Andheri West",
                shipping_address="Flat 101, Galaxy Apartments, Andheri West",
                city="Mumbai",
                state="Maharashtra",
                pincode="400053",
                phone="9988776655",
                email="rahul@example.com",
                gstin="27XYZAB9876C1Z4"
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)
            print(f"Customer created: {customer.name}")
        else:
            print(f"Customer exists: {customer.name}")

        # 3. Create Products
        products_data = [
            {"name": "Wooden Dining Table", "hsn": "9403", "rate": 15000.0, "gst": 18.0, "unit": "Nos"},
            {"name": "Office Chair Ergonomic", "hsn": "9401", "rate": 4500.0, "gst": 18.0, "unit": "Nos"},
            {"name": "Queen Size Bed", "hsn": "9403", "rate": 25000.0, "gst": 18.0, "unit": "Nos"}
        ]
        
        created_products = []
        for p_data in products_data:
            product = db.query(Product).filter(Product.name == p_data["name"]).first()
            if not product:
                product = Product(
                    shop_id=shop.id,
                    name=p_data["name"],
                    hsn_code=p_data["hsn"],
                    rate=p_data["rate"],
                    gst_rate=p_data["gst"],
                    unit=p_data["unit"]
                )
                db.add(product)
                db.commit()
                db.refresh(product)
                print(f"Product created: {product.name}")
            else:
                print(f"Product exists: {product.name}")
            created_products.append(product)

        # 4. Create Invoice
        # Check if invoice already exists to avoid duplicates
        existing_invoice = db.query(Invoice).filter(Invoice.invoice_no == "INV-001").first()
        if existing_invoice:
            print("Test invoice INV-001 already exists.")
            return existing_invoice.id

        invoice = Invoice(
            shop_id=shop.id,
            customer_id=customer.id,
            invoice_no="INV-001",
            date=date.today(),
            place_of_supply="Maharashtra",
            status="Generated"
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        # Add Items
        items = [
            {"product": created_products[0], "qty": 1}, # Dining Table
            {"product": created_products[1], "qty": 4}, # Chairs
        ]

        total_taxable = 0
        total_cgst = 0
        total_sgst = 0
        total_igst = 0
        grand_total = 0

        for item_data in items:
            product = item_data["product"]
            qty = item_data["qty"]
            rate = product.rate
            taxable_value = rate * qty
            
            # Intra-state (Same state) -> CGST + SGST
            cgst_rate = product.gst_rate / 2
            sgst_rate = product.gst_rate / 2
            cgst_amt = taxable_value * (cgst_rate / 100)
            sgst_amt = taxable_value * (sgst_rate / 100)
            igst_amt = 0
            
            item_total = taxable_value + cgst_amt + sgst_amt

            inv_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=product.id,
                description=product.name,
                hsn_code=product.hsn_code,
                qty=qty,
                unit=product.unit,
                rate=rate,
                taxable_value=taxable_value,
                tax_rate=product.gst_rate,
                cgst_amount=cgst_amt,
                sgst_amount=sgst_amt,
                igst_amount=igst_amt,
                total_amount=item_total
            )
            db.add(inv_item)
            
            total_taxable += taxable_value
            total_cgst += cgst_amt
            total_sgst += sgst_amt
            total_igst += igst_amt
            grand_total += item_total

        # Update Invoice Totals
        invoice.taxable_amount = total_taxable
        invoice.cgst_amount = total_cgst
        invoice.sgst_amount = total_sgst
        invoice.igst_amount = total_igst
        invoice.grand_total = grand_total
        invoice.amount_in_words = "Thirty Eight Thousand Nine Hundred Forty Only" # Hardcoded for simplicity
        
        db.commit()
        print(f"Invoice created: {invoice.invoice_no} with Total: {invoice.grand_total}")
        return invoice.id

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
