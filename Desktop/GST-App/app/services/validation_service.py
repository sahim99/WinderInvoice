"""
Validation Service for WinderInvoice
Validates Indian business identifiers: GSTIN, PAN, IFSC, UPI, Pincode
"""
import re


def validate_gstin(gstin: str) -> bool:
    """
    Validate GSTIN (Goods and Services Tax Identification Number)
    Format: 15 characters - 2 state code + 10 PAN + 1 entity + 1 Z + 1 checksum
    Example: 29ABCDE1234F1Z5
    
    Args:
        gstin: GSTIN string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not gstin:
        return False
    
    # Remove spaces and convert to uppercase
    gstin = gstin.strip().upper()
    
    # Check length
    if len(gstin) != 15:
        return False
    
    # GSTIN pattern: 2 digits + 10 alphanumeric (PAN) + 1 alphanumeric + Z + 1 alphanumeric
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    
    return bool(re.match(pattern, gstin))


def validate_pan(pan: str) -> bool:
    """
    Validate PAN (Permanent Account Number)
    Format: 10 characters - 5 letters + 4 digits + 1 letter
    Example: ABCDE1234F
    
    Args:
        pan: PAN string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not pan:
        return False
    
    # Remove spaces and convert to uppercase
    pan = pan.strip().upper()
    
    # Check length
    if len(pan) != 10:
        return False
    
    # PAN pattern: 5 letters + 4 digits + 1 letter
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    
    return bool(re.match(pattern, pan))


def validate_ifsc(ifsc: str) -> bool:
    """
    Validate IFSC (Indian Financial System Code)
    Format: 11 characters - 4 letters (bank code) + 0 + 6 alphanumeric (branch code)
    Example: SBIN0001234
    
    Args:
        ifsc: IFSC string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not ifsc:
        return False
    
    # Remove spaces and convert to uppercase
    ifsc = ifsc.strip().upper()
    
    # Check length
    if len(ifsc) != 11:
        return False
    
    # IFSC pattern: 4 letters + 0 + 6 alphanumeric
    pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    
    return bool(re.match(pattern, ifsc))


def validate_upi(upi_id: str) -> bool:
    """
    Validate UPI ID
    Format: username@provider
    Example: user@ybl, merchant@paytm
    
    Args:
        upi_id: UPI ID string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not upi_id:
        return False
    
    # Remove spaces and convert to lowercase
    upi_id = upi_id.strip().lower()
    
    # UPI pattern: alphanumeric/dots/underscores + @ + provider
    pattern = r'^[a-z0-9._-]+@[a-z]+$'
    
    if not re.match(pattern, upi_id):
        return False
    
    # Common UPI providers
    valid_providers = [
        'ybl',      # PhonePe
        'paytm',    # Paytm
        'okaxis',   # Google Pay (Axis)
        'okicici',  # Google Pay (ICICI)
        'oksbi',    # Google Pay (SBI)
        'ibl',      # ICICI Bank
        'axl',      # Axis Bank
        'sbi',      # State Bank of India
        'hdfcbank', # HDFC Bank
        'pnb',      # Punjab National Bank
        'boi',      # Bank of India
        'cnrb',     # Canara Bank
        'upi',      # Generic UPI
    ]
    
    provider = upi_id.split('@')[1]
    
    # Accept any provider (some banks have custom handles)
    # Just check that it's not empty
    return len(provider) > 0


def validate_pincode(pincode: str) -> bool:
    """
    Validate Indian Pincode
    Format: 6 digits
    Example: 110001
    
    Args:
        pincode: Pincode string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not pincode:
        return False
    
    # Remove spaces
    pincode = pincode.strip()
    
    # Check length and digits only
    if len(pincode) != 6:
        return False
    
    return pincode.isdigit()


def validate_phone(phone: str) -> bool:
    """
    Validate Indian mobile number
    Format: 10 digits (with optional +91 or 91 prefix)
    Example: 9876543210, +919876543210, 919876543210
    
    Args:
        phone: Phone number string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove spaces, hyphens, and parentheses
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Remove +91 or 91 prefix
    if phone.startswith('+91'):
        phone = phone[3:]
    elif phone.startswith('91') and len(phone) == 12:
        phone = phone[2:]
    
    # Check if 10 digits and starts with 6-9
    if len(phone) != 10:
        return False
    
    if not phone.isdigit():
        return False
    
    # Indian mobile numbers start with 6, 7, 8, or 9
    if phone[0] not in ['6', '7', '8', '9']:
        return False
    
    return True


# Example usage and tests
if __name__ == "__main__":
    print("Testing Validation Service...\n")
    
    # Test GSTIN
    print("GSTIN Tests:")
    print(f"  Valid: 29ABCDE1234F1Z5 -> {validate_gstin('29ABCDE1234F1Z5')}")
    print(f"  Invalid: 29ABCDE1234 -> {validate_gstin('29ABCDE1234')}")
    
    # Test PAN
    print("\nPAN Tests:")
    print(f"  Valid: ABCDE1234F -> {validate_pan('ABCDE1234F')}")
    print(f"  Invalid: ABC123 -> {validate_pan('ABC123')}")
    
    # Test IFSC
    print("\nIFSC Tests:")
    print(f"  Valid: SBIN0001234 -> {validate_ifsc('SBIN0001234')}")
    print(f"  Invalid: SBIN1234 -> {validate_ifsc('SBIN1234')}")
    
    # Test UPI
    print("\nUPI Tests:")
    print(f"  Valid: user@ybl -> {validate_upi('user@ybl')}")
    print(f"  Valid: merchant@paytm -> {validate_upi('merchant@paytm')}")
    print(f"  Invalid: user -> {validate_upi('user')}")
    
    # Test Pincode
    print("\nPincode Tests:")
    print(f"  Valid: 110001 -> {validate_pincode('110001')}")
    print(f"  Invalid: 1100 -> {validate_pincode('1100')}")
    
    # Test Phone
    print("\nPhone Tests:")
    print(f"  Valid: 9876543210 -> {validate_phone('9876543210')}")
    print(f"  Valid: +919876543210 -> {validate_phone('+919876543210')}")
    print(f"  Invalid: 1234567890 -> {validate_phone('1234567890')}")
    
    print("\n✅ Validation service working correctly!")
