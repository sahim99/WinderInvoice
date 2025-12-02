from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "staff"

class UserCreate(UserBase):
    password: str
    shop_id: int

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(UserBase):
    id: int
    shop_id: int
    is_active: bool

    class Config:
        orm_mode = True

# Shop Schemas
class ShopBase(BaseModel):
    name: str
    gstin: str
    address: str
    city: str
    state: str
    state_code: str
    pincode: str
    phone: str
    email: str

class ShopCreate(ShopBase):
    pass

class ShopOut(ShopBase):
    id: int
    logo_url: Optional[str] = None

    class Config:
        orm_mode = True

# Customer Schemas
class CustomerBase(BaseModel):
    name: str
    billing_address: str
    shipping_address: str
    gstin: Optional[str] = None
    state: str
    state_code: str
    party_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerOut(CustomerBase):
    id: int
    shop_id: int
    opening_balance: float

    class Config:
        orm_mode = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    hsn_code: str
    unit: str
    rate: float
    gst_rate: float

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    shop_id: int
    is_active: bool

    class Config:
        orm_mode = True

# Invoice Schemas
class InvoiceItemBase(BaseModel):
    product_id: Optional[int] = None
    description: str
    hsn_code: str
    qty: float
    unit: str
    rate: float
    discount_amount: float = 0.0
    tax_rate: float

class InvoiceCreate(BaseModel):
    customer_id: int
    date: date
    place_of_supply: str
    vehicle_no: Optional[str] = None
    eway_bill_no: Optional[str] = None
    items: List[InvoiceItemBase]

class InvoiceOut(BaseModel):
    id: int
    invoice_no: str
    date: date
    grand_total: float
    customer: CustomerOut
    
    class Config:
        orm_mode = True
