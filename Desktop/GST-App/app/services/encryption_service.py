"""
Encryption Service for WinderInvoice
Handles encryption/decryption of sensitive data like bank account numbers
"""
from cryptography.fernet import Fernet
import os
import base64

# Generate or load encryption key
# In production, this should be stored in environment variables or a secure key management service
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    # Generate a key for development (DO NOT use in production)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"⚠️  WARNING: Using generated encryption key. Set ENCRYPTION_KEY environment variable in production!")
    print(f"Generated key: {ENCRYPTION_KEY}")

# Initialize Fernet cipher
cipher = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


def encrypt_account_number(account_number: str) -> str:
    """
    Encrypt a bank account number
    
    Args:
        account_number: Plain text account number
        
    Returns:
        Encrypted account number as base64 string
    """
    if not account_number:
        return ""
    
    # Convert to bytes and encrypt
    encrypted = cipher.encrypt(account_number.encode())
    
    # Return as base64 string for database storage
    return base64.b64encode(encrypted).decode()


def decrypt_account_number(encrypted_account_number: str) -> str:
    """
    Decrypt a bank account number
    
    Args:
        encrypted_account_number: Encrypted account number (base64 string)
        
    Returns:
        Plain text account number
    """
    if not encrypted_account_number:
        return ""
    
    try:
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_account_number.encode())
        
        # Decrypt
        decrypted = cipher.decrypt(encrypted_bytes)
        
        return decrypted.decode()
    except Exception as e:
        print(f"Error decrypting account number: {e}")
        return ""


def mask_account_number(account_number: str) -> str:
    """
    Mask account number for display
    Shows only last 4 digits
    
    Args:
        account_number: Plain text account number
        
    Returns:
        Masked account number (e.g., "**** **** 1234")
    """
    if not account_number or len(account_number) < 4:
        return "****"
    
    # Get last 4 digits
    last_four = account_number[-4:]
    
    # Calculate number of asterisk groups needed
    masked_length = len(account_number) - 4
    num_groups = (masked_length + 3) // 4  # Round up to nearest group of 4
    
    # Create masked string
    masked = " ".join(["****"] * num_groups) + " " + last_four
    
    return masked


def hash_token(token: str) -> str:
    """
    Hash an API token for storage
    Uses SHA-256 for one-way hashing
    
    Args:
        token: Plain text token
        
    Returns:
        Hashed token
    """
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()


# Example usage and tests
if __name__ == "__main__":
    # Test encryption/decryption
    test_account = "1234567890123456"
    
    print(f"Original: {test_account}")
    
    encrypted = encrypt_account_number(test_account)
    print(f"Encrypted: {encrypted}")
    
    decrypted = decrypt_account_number(encrypted)
    print(f"Decrypted: {decrypted}")
    
    masked = mask_account_number(test_account)
    print(f"Masked: {masked}")
    
    assert test_account == decrypted, "Encryption/decryption failed!"
    print("\n✅ Encryption service working correctly!")
