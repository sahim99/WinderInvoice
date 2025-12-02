from fastapi import APIRouter, Depends, Request, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_shop, get_current_user
from app import models, schemas
from typing import Optional

router = APIRouter(tags=["masters"])
templates = Jinja2Templates(directory="app/templates")

# --- Customers ---

@router.get("/customers")
def list_customers(request: Request, user: models.User = Depends(get_current_user), shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    customers = db.query(models.Customer).filter(models.Customer.shop_id == shop.id).all()
    return templates.TemplateResponse("customers/list.html", {"request": request, "user": user, "customers": customers, "title": "Customers"})

@router.get("/customers/new")
def new_customer(request: Request, user: models.User = Depends(get_current_user)):
    return templates.TemplateResponse("customers/create.html", {"request": request, "user": user, "title": "New Customer"})

@router.post("/customers/new")
def create_customer(
    request: Request,
    name: str = Form(...),
    contact_person: Optional[str] = Form(None),
    billing_address: str = Form(...),
    city: str = Form(...),
    pincode: Optional[str] = Form(None),
    shipping_address: str = Form(...),
    gstin: Optional[str] = Form(None),
    pan: Optional[str] = Form(None),
    state: str = Form(...),
    state_code: str = Form(...),
    place_of_supply: str = Form(...),
    party_code: Optional[str] = Form(None),
    price_category: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    opening_balance: float = Form(0.0),
    shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    customer = models.Customer(
        shop_id=shop.id,
        name=name,
        contact_person=contact_person,
        billing_address=billing_address,
        city=city,
        pincode=pincode,
        shipping_address=shipping_address,
        gstin=gstin,
        pan=pan,
        state=state,
        state_code=state_code,
        place_of_supply=place_of_supply,
        party_code=party_code,
        price_category=price_category,
        phone=phone,
        email=email,
        opening_balance=opening_balance
    )
    db.add(customer)
    db.commit()
    return RedirectResponse(url="/customers", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/customers/{customer_id}/edit")
def edit_customer(customer_id: int, request: Request, user: models.User = Depends(get_current_user), shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id, models.Customer.shop_id == shop.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return templates.TemplateResponse("customers/edit.html", {"request": request, "user": user, "customer": customer, "title": "Edit Customer"})

@router.post("/customers/{customer_id}/edit")
def update_customer(
    customer_id: int,
    request: Request,
    name: str = Form(...),
    contact_person: Optional[str] = Form(None),
    billing_address: str = Form(...),
    city: str = Form(...),
    pincode: Optional[str] = Form(None),
    shipping_address: str = Form(...),
    gstin: Optional[str] = Form(None),
    pan: Optional[str] = Form(None),
    state: str = Form(...),
    state_code: str = Form(...),
    place_of_supply: str = Form(...),
    party_code: Optional[str] = Form(None),
    price_category: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    opening_balance: float = Form(0.0),
    shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id, models.Customer.shop_id == shop.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer.name = name
    customer.contact_person = contact_person
    customer.billing_address = billing_address
    customer.city = city
    customer.pincode = pincode
    customer.shipping_address = shipping_address
    customer.gstin = gstin
    customer.pan = pan
    customer.state = state
    customer.state_code = state_code
    customer.place_of_supply = place_of_supply
    customer.party_code = party_code
    customer.price_category = price_category
    customer.phone = phone
    customer.email = email
    customer.opening_balance = opening_balance
    
    db.commit()
    return RedirectResponse(url="/customers", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/customers/{customer_id}/delete")
def delete_customer(customer_id: int, shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id, models.Customer.shop_id == shop.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return RedirectResponse(url="/customers", status_code=status.HTTP_303_SEE_OTHER)

# --- Products ---

@router.get("/products")
def list_products(request: Request, user: models.User = Depends(get_current_user), shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.shop_id == shop.id).all()
    return templates.TemplateResponse("products/list.html", {"request": request, "user": user, "products": products, "title": "Products"})

@router.get("/products/new")
def new_product(request: Request, user: models.User = Depends(get_current_user)):
    return templates.TemplateResponse("products/create.html", {"request": request, "user": user, "title": "New Product"})

@router.post("/products/new")
def create_product(
    request: Request,
    name: str = Form(...),
    hsn_code: str = Form(...),
    unit: str = Form(...),
    rate: float = Form(...),
    gst_rate: float = Form(...),
    description: Optional[str] = Form(None),
    shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    product = models.Product(
        shop_id=shop.id,
        name=name,
        hsn_code=hsn_code,
        unit=unit,
        rate=rate,
        gst_rate=gst_rate,
        description=description
    )
    db.add(product)
    db.commit()
    return RedirectResponse(url="/products", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/products/{product_id}/edit")
def edit_product(product_id: int, request: Request, user: models.User = Depends(get_current_user), shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.shop_id == shop.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return templates.TemplateResponse("products/edit.html", {"request": request, "user": user, "product": product, "title": "Edit Product"})

@router.post("/products/{product_id}/edit")
def update_product(
    product_id: int,
    request: Request,
    name: str = Form(...),
    hsn_code: str = Form(...),
    unit: str = Form(...),
    rate: float = Form(...),
    gst_rate: float = Form(...),
    description: Optional[str] = Form(None),
    shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.shop_id == shop.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.name = name
    product.hsn_code = hsn_code
    product.unit = unit
    product.rate = rate
    product.gst_rate = gst_rate
    product.description = description
    
    db.commit()
    return RedirectResponse(url="/products", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/products/{product_id}/delete")
def delete_product(product_id: int, shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.shop_id == shop.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return RedirectResponse(url="/products", status_code=status.HTTP_303_SEE_OTHER)
