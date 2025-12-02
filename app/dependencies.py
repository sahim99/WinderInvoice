from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app import models
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    token = request.cookies.get("access_token")
    print(f"DEBUG: get_current_user path={request.url.path} cookies={request.cookies}")
    if not token:
        # Check if it's a bearer token (optional, for API clients)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
         print(f"DEBUG: No token found for {request.url.path}")
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    # DEMO MODE RESTRICTION
    if user.email == "demo@winderinvoice.com" and request.method not in ["GET", "HEAD", "OPTIONS"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Demo Mode is Read-Only. You cannot modify data."
        )
    
    return user

def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_shop(current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)) -> models.Shop:
    shop = db.query(models.Shop).filter(models.Shop.id == current_user.shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop
