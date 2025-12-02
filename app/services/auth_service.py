# app/services/auth_service.py
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from app.config import settings
from fastapi import HTTPException

# bcrypt limit in bytes
BCRYPT_MAX_BYTES = 72

def _truncate_password_to_72_bytes(password: str) -> bytes:
    """
    Return a bytes object of password truncated so its UTF-8 encoding
    is at most 72 bytes. This avoids bcrypt ValueError.
    """
    if password is None:
        password = ""
    if not isinstance(password, str):
        password = str(password)
    b = password.encode("utf-8")
    if len(b) <= BCRYPT_MAX_BYTES:
        return b
    # slice bytes and drop incomplete trailing multi-byte char
    truncated = b[:BCRYPT_MAX_BYTES].decode("utf-8", errors="ignore")
    return truncated.encode("utf-8")

def get_password_hash(password: str) -> str:
    """
    Hash using bcrypt directly.
    Returns the hash as a utf-8 string (decoded).
    """
    safe_bytes = _truncate_password_to_72_bytes(password)
    try:
        hashed = bcrypt.hashpw(safe_bytes, bcrypt.gensalt())
        return hashed.decode("utf-8")
    except Exception as e:
        # log or re-raise as needed
        print(f"[auth_service.get_password_hash] ERROR: {e}")
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against an existing bcrypt hash.
    Truncates plaintext consistently before verify.
    """
    try:
        safe_bytes = _truncate_password_to_72_bytes(plain_password)
        return bcrypt.checkpw(safe_bytes, hashed_password.encode("utf-8"))
    except Exception as e:
        print(f"[auth_service.verify_password] ERROR: {e}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
