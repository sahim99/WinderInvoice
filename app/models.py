# app/models.py
from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, Float, Text, Date, JSON,
    DateTime, Enum as SAEnum, func
)
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

# ---------- ENUMS ----------
class UserRoleEnum(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"

# ---------- USER ----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Legacy/basic
    name = Column(String, nullable=True)             # legacy field
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True, unique=True)
    phone_verified = Column(Boolean, default=False)

    # Security
    hashed_password = Column(String, nullable=True)
    role = Column(SAEnum(UserRoleEnum), default=UserRoleEnum.ADMIN)
    is_active = Column(Boolean, default=True)

    # Preferences
    avatar_path = Column(String, nullable=True)
    language = Column(String, default="English")
    timezone = Column(String, default="Asia/Kolkata")

    # relations
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=True)
    shop = relationship("Shop", back_populates="users")

    notification_preferences = relationship(
        "NotificationPreference", back_populates="user", uselist=False
    )

    api_tokens = relationship("APIToken", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# ---------- SHOP ----------
class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    logo_path = Column(String, nullable=True)
    signature_path = Column(String, nullable=True)

    # Business info
    gstin = Column(String(15), nullable=True, index=True)
    pan = Column(String(10), nullable=True, index=True)
    business_email = Column(String, nullable=True)
    business_phone = Column(String, nullable=True)
    category = Column(String, nullable=True)

    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String(10), nullable=True)
    place_of_supply = Column(String, nullable=True)

    website = Column(String, nullable=True)

    # Invoice defaults
    invoice_prefix = Column(String, default="WINV-")
    next_invoice_number = Column(Integer, default=1)

    # relationships
    users = relationship("User", back_populates="shop")
    customers = relationship("Customer", back_populates="shop")
    products = relationship("Product", back_populates="shop")
    invoices = relationship("Invoice", back_populates="shop")
    bank_details = relationship("BankDetail", back_populates="shop", cascade="all, delete-orphan")
    branches = relationship("Branch", back_populates="shop")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# ---------- BANK DETAIL ----------
class BankDetail(Base):
    __tablename__ = "bank_details"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"))
    account_holder = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)
    # IMPORTANT: store encrypted account number (use encryption_service)
    account_number_encrypted = Column(String, nullable=False)
    ifsc = Column(String, nullable=True, index=True)
    branch_name = Column(String, nullable=True)
    upi_id = Column(String, nullable=True)
    qr_code_path = Column(String, nullable=True)
    payment_note = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    shop = relationship("Shop", back_populates="bank_details")

# ---------- NOTIFICATION PREFERENCES ----------
class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    invoice_email = Column(Boolean, default=True)
    invoice_whatsapp = Column(Boolean, default=False)
    monthly_gst_summary = Column(Boolean, default=True)
    payment_alerts = Column(Boolean, default=True)

    user = relationship("User", back_populates="notification_preferences")

# ---------- BRANCH (multi-store) ----------
class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"))
    name = Column(String, nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    gstin = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    shop = relationship("Shop", back_populates="branches")

# ---------- API TOKENS ----------
class APIToken(Base):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=True)
    token_hash = Column(String, nullable=False)  # store only hashed token
    scopes = Column(JSON, nullable=True)         # list of scopes
    revoked = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="api_tokens")

# ---------- AUDIT LOG ----------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    object_type = Column(String, nullable=True)
    object_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="audit_logs")

# ---------- EXISTING DOMAIN MODELS ----------
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"))
    name = Column(String, index=True, nullable=False)
    contact_person = Column(String, nullable=True)
    billing_address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    shipping_address = Column(Text, nullable=True)
    gstin = Column(String, nullable=True)
    pan = Column(String, nullable=True)
    state = Column(String, nullable=True)
    state_code = Column(String, nullable=True)
    place_of_supply = Column(String, nullable=True)
    party_code = Column(String, nullable=True)
    price_category = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    opening_balance = Column(Float, default=0.0)

    shop = relationship("Shop", back_populates="customers")
    invoices = relationship("Invoice", back_populates="customer")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"))
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    hsn_code = Column(String, nullable=True)
    unit = Column(String, nullable=True)  # pcs, set, etc.
    rate = Column(Float, default=0.0)
    gst_rate = Column(Float, default=0.0) # 5,12,18,28
    is_active = Column(Boolean, default=True)

    shop = relationship("Shop", back_populates="products")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    invoice_no = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=True)
    place_of_supply = Column(String, nullable=True)
    vehicle_no = Column(String, nullable=True)
    eway_bill_no = Column(String, nullable=True)

    # Totals
    taxable_amount = Column(Float, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    round_off = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    amount_in_words = Column(String, nullable=True)

    # Status
    status = Column(String, default="Generated") # Generated, Paid, Cancelled

    shop = relationship("Shop", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    description = Column(String, nullable=True)
    hsn_code = Column(String, nullable=True)
    no_of_pkts = Column(Integer, default=0)
    qty = Column(Float, default=0.0)
    unit = Column(String, nullable=True)
    rate = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    taxable_value = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)

    invoice = relationship("Invoice", back_populates="items")
