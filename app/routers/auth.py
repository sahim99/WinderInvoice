from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import auth_service
from app.config import settings
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

# State code mapping for Indian states
STATE_CODES = {
    "Andhra Pradesh": "37",
    "Arunachal Pradesh": "12",
    "Assam": "18",
    "Bihar": "10",
    "Chhattisgarh": "22",
    "Goa": "30",
    "Gujarat": "24",
    "Haryana": "06",
    "Himachal Pradesh": "02",
    "Jharkhand": "20",
    "Karnataka": "29",
    "Kerala": "32",
    "Madhya Pradesh": "23",
    "Maharashtra": "27",
    "Manipur": "14",
    "Meghalaya": "17",
    "Mizoram": "15",
    "Nagaland": "13",
    "Odisha": "21",
    "Punjab": "03",
    "Rajasthan": "08",
    "Sikkim": "11",
    "Tamil Nadu": "33",
    "Telangana": "36",
    "Tripura": "16",
    "Uttar Pradesh": "09",
    "Uttarakhand": "05",
    "West Bengal": "19",
}

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth_service.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Invalid credentials"})
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response

@router.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})

@router.post("/signup")
def signup(
    request: Request,
    full_name: str = Form(...),
    shop_name: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    gstin: str = Form(None),
    city: str = Form(...),
    state: str = Form(...),
    db: Session = Depends(get_db)
):
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse("auth/signup.html", {
            "request": request, 
            "error": "Passwords do not match!"
        })

    # Validate password length (bcrypt limit)
    if len(password.encode("utf-8")) > 72:
        return templates.TemplateResponse("auth/signup.html", {
            "request": request, 
            "error": "Password too long. Please use a password shorter than 72 bytes."
        })
    
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("auth/signup.html", {
            "request": request, 
            "error": "Email already registered. Please sign in instead."
        })
    
    # Get state code
    state_code = STATE_CODES.get(state, "00")
    
    # Create shop
    shop = models.Shop(
        name=shop_name,
        gstin=gstin if gstin else None,
        address_line1="",  # Can be updated later in settings
        city=city,
        state=state,
        pincode="",  # Can be updated later
        business_phone=mobile,
        business_email=email
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    
    # Create user with hashed password
    hashed_password = auth_service.get_password_hash(password)
    user = models.User(
        shop_id=shop.id,
        name=full_name,
        email=email,
        hashed_password=hashed_password,
        role=models.UserRoleEnum.ADMIN
    )
    db.add(user)
    db.commit()
    
    # Redirect to login with success message
    return RedirectResponse(url="/auth/login?signup=success", status_code=status.HTTP_302_FOUND)

@router.get("/demo")
def demo_login(response: Response, db: Session = Depends(get_db)):
    """One-click login for Demo Mode"""
    demo_email = "demo@winderinvoice.com"
    
    # Check if demo user exists
    user = db.query(models.User).filter(models.User.email == demo_email).first()
    
    if not user:
        # Create Demo Shop if not exists
        shop = models.Shop(
            name="Winder Demo Store",
            gstin="29ABCDE1234F1Z5",
            address_line1="123, Tech Park, Indiranagar",
            city="Bengaluru",
            state="Karnataka",
            pincode="560038",
            business_phone="9876543210",
            business_email="demo@winderinvoice.com"
        )
        db.add(shop)
        db.commit()
        db.refresh(shop)
        
        # Create Demo User
        hashed_password = auth_service.get_password_hash("demo123")
        user = models.User(
            shop_id=shop.id,
            name="Demo User",
            email=demo_email,
            hashed_password=hashed_password,
            role=models.UserRoleEnum.ADMIN
        )
        db.add(user)
        db.commit()
    
    # Login logic
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response

@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@router.get("/setup")
def setup_initial_data(db: Session = Depends(get_db)):
    # Check if shop exists
    shop = db.query(models.Shop).first()
    if not shop:
        shop = models.Shop(
            name="My Furniture Shop",
            gstin="19AAAPJ2698R1ZO",
            address_line1="123, Furniture Market",
            city="Kolkata",
            state="West Bengal",
            pincode="700001",
            business_phone="9876543210",
            business_email="shop@example.com"
        )
        db.add(shop)
        db.commit()
        db.refresh(shop)
    
    # Check if user exists
    user = db.query(models.User).filter(models.User.email == "admin@example.com").first()
    if not user:
        hashed_password = auth_service.get_password_hash("admin123")
        user = models.User(
            shop_id=shop.id,
            name="Admin User",
            email="admin@example.com",
            hashed_password=hashed_password,
            role=models.UserRoleEnum.ADMIN
        )
        db.add(user)
        db.commit()
        return {"message": "Initial data created. Login with admin@example.com / admin123"}
    
    return {"message": "Data already exists"}
