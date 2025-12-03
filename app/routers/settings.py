"""
Settings Router for WinderInvoice
Handles profile, shop, banking, security, and notification settings.
Updated to use storage abstraction for S3/local file uploads.
"""

from fastapi import (
    APIRouter, Depends, HTTPException, status, Request, Form,
    UploadFile, File
)
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path
from datetime import datetime
import uuid

from app.database import get_db
from app import models
from app.dependencies import get_current_user
from app.services import validation_service, encryption_service
from app.services.auth_service import get_password_hash, verify_password
from app.storage import save_upload, get_file_url  # NEW: Use storage abstraction

router = APIRouter(prefix="/settings", tags=["settings"])
templates = Jinja2Templates(directory="app/templates")

# ========== UPLOAD CONFIG ==========
# Allowed extensions & size
ALLOWED_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
MAX_UPLOAD_BYTES = 4 * 1024 * 1024  # 4 MB


# ========== HELPERS ==========
def _parse_bool_from_form(val: Optional[str]) -> bool:
    """Parse checkbox/form boolean values safely."""
    return True if val in ("on", "true", "1", True) else False


def save_upload_file(upload_file: UploadFile, subdirectory: str, prefix: str) -> str:
    """
    Save uploaded file using storage abstraction (S3 or local).
    Returns accessible URL/path for the file.
    
    Args:
        upload_file: FastAPI UploadFile object
        subdirectory: Folder name (e.g., 'logos', 'avatars', 'qr_codes')
        prefix: Filename prefix (e.g., 'shop_1', 'user_5')
    
    Returns:
        Web-accessible URL or path
    
    Raises:
        HTTPException: On validation errors or upload failures
    """
    if upload_file is None:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Sanitize filename and extension
    orig_name = Path(upload_file.filename or "").name
    if "." not in orig_name:
        raise HTTPException(status_code=400, detail="Filename missing extension")

    ext = Path(orig_name).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXT:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # Basic content-type check (allow svg via extension)
    if not upload_file.content_type.startswith("image/") and ext != ".svg":
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    # Validate file size by reading in chunks
    upload_file.file.seek(0)  # Reset file pointer
    file_size = 0
    chunk_size = 1024 * 64  # 64KB chunks
    
    # Create temporary file-like object to validate size
    chunks = []
    while True:
        chunk = upload_file.file.read(chunk_size)
        if not chunk:
            break
        file_size += len(chunk)
        if file_size > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=400, detail="File too large (max 4 MB)")
        chunks.append(chunk)
    
    # Reset file pointer and create a bytes object
    upload_file.file.seek(0)

    # Create unique filename
    uid = uuid.uuid4().hex
    safe_name = f"{prefix}_{uid}{ext}"
    file_path = f"{subdirectory}/{safe_name}"

    try:
        # Use storage abstraction - automatically handles S3 or local storage
        web_path = save_upload(upload_file.file, file_path)
        return web_path
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed saving file: {str(e)}")
    finally:
        # Ensure file pointer is closed
        try:
            upload_file.file.close()
        except Exception:
            pass


# ========== MAIN SETTINGS PAGE ==========
@router.get("/", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Main settings page with sidebar navigation (defaults to profile tab)."""
    return templates.TemplateResponse("settings/index.html", {
        "request": request,
        "user": user,
        "active_tab": "profile"
    })


# ========== PROFILE ENDPOINTS ==========
@router.get("/profile", response_class=HTMLResponse)
async def get_profile(
    request: Request,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Render Profile tab (profile form + notification prefs)."""
    notif_prefs = db.query(models.NotificationPreference).filter(
        models.NotificationPreference.user_id == user.id
    ).first()

    return templates.TemplateResponse("settings/profile.html", {
        "request": request,
        "user": user,
        "notification_preferences": notif_prefs,
        "active_tab": "profile"
    })


@router.post("/profile")
async def update_profile(
    request: Request,
    full_name: str = Form(...),
    phone: Optional[str] = Form(None),
    language: str = Form("English"),
    timezone: str = Form("Asia/Kolkata"),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile with phone uniqueness check and basic validation."""
    try:
        if phone:
            if not validation_service.validate_phone(phone):
                raise HTTPException(status_code=400, detail="Invalid phone number format")

            existing_user = db.query(models.User).filter(
                models.User.phone == phone,
                models.User.id != user.id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Phone number already in use")

        user.full_name = full_name
        user.name = full_name  # Sync legacy field
        user.phone = phone
        user.language = language
        user.timezone = timezone
        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)
        return RedirectResponse(url="/settings/profile?success=Profile updated successfully", status_code=303)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")


@router.post("/profile/avatar")
async def upload_avatar(
    avatar: UploadFile = File(...),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload user avatar using storage abstraction (S3 or local)."""
    try:
        # Save file using storage abstraction
        avatar_web_path = save_upload_file(avatar, "avatars", f"user_{user.id}")

        # Update user record
        user.avatar_path = avatar_web_path
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return JSONResponse({"success": True, "avatar_path": avatar_web_path})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading avatar: {str(e)}")


# ========== SHOP SETTINGS ENDPOINTS ==========
@router.get("/shop", response_class=HTMLResponse)
async def get_shop_settings(
    request: Request,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Render Shop Settings tab."""
    shop = getattr(user, "shop", None)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    return templates.TemplateResponse("settings/shop.html", {
        "request": request,
        "user": user,
        "shop": shop,
        "active_tab": "shop"
    })


@router.post("/shop")
async def update_shop_settings(
    request: Request,
    name: str = Form(...),
    gstin: Optional[str] = Form(None),
    pan: Optional[str] = Form(None),
    business_email: Optional[str] = Form(None),
    business_phone: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    address_line1: Optional[str] = Form(None),
    address_line2: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),
    place_of_supply: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    invoice_prefix: str = Form("WINV-"),
    next_invoice_number: int = Form(1),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update shop settings with server-side validation."""
    try:
        shop = getattr(user, "shop", None)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop not found")

        if gstin and not validation_service.validate_gstin(gstin):
            raise HTTPException(status_code=400, detail="Invalid GSTIN format")
        if pan and not validation_service.validate_pan(pan):
            raise HTTPException(status_code=400, detail="Invalid PAN format")
        if pincode and not validation_service.validate_pincode(pincode):
            raise HTTPException(status_code=400, detail="Invalid pincode format")
        if business_phone and not validation_service.validate_phone(business_phone):
            raise HTTPException(status_code=400, detail="Invalid business phone format")

        # Update shop fields
        shop.name = name
        shop.gstin = gstin
        shop.pan = pan
        shop.business_email = business_email
        shop.business_phone = business_phone
        shop.category = category
        shop.address_line1 = address_line1
        shop.address_line2 = address_line2
        shop.city = city
        shop.state = state
        shop.pincode = pincode
        shop.place_of_supply = place_of_supply
        shop.website = website
        shop.invoice_prefix = invoice_prefix
        shop.next_invoice_number = next_invoice_number
        shop.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(shop)
        return RedirectResponse(url="/settings/shop?success=Shop settings updated successfully", status_code=303)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating shop settings: {str(e)}")


@router.post("/shop/logo")
async def upload_shop_logo(
    logo: UploadFile = File(...),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload shop logo using storage abstraction (S3 or local)."""
    try:
        shop = getattr(user, "shop", None)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop not found")

        # Save using storage abstraction
        logo_web_path = save_upload_file(logo, "logos", f"shop_{shop.id}")
        shop.logo_path = logo_web_path
        shop.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(shop)

        return JSONResponse({"success": True, "logo_path": logo_web_path})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading logo: {str(e)}")


@router.post("/shop/signature")
async def upload_signature(
    signature: UploadFile = File(...),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload digital signature image using storage abstraction."""
    try:
        shop = getattr(user, "shop", None)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop not found")

        # Save using storage abstraction
        sig_web_path = save_upload_file(signature, "signatures", f"shop_{shop.id}")
        shop.signature_path = sig_web_path
        shop.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(shop)

        return JSONResponse({"success": True, "signature_path": sig_web_path})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading signature: {str(e)}")


# ========== BANKING & PAYMENTS ENDPOINTS ==========
@router.get("/bank", response_class=HTMLResponse)
async def get_bank_details(
    request: Request,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Render banking tab; show masked account number if present."""
    shop = getattr(user, "shop", None)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    bank_details = db.query(models.BankDetail).filter(
        models.BankDetail.shop_id == shop.id
    ).first()

    if bank_details and bank_details.account_number_encrypted:
        try:
            decrypted = encryption_service.decrypt_account_number(bank_details.account_number_encrypted)
            bank_details.account_number_masked = encryption_service.mask_account_number(decrypted)
        except Exception:
            bank_details.account_number_masked = None

    return templates.TemplateResponse("settings/banking.html", {
        "request": request,
        "user": user,
        "shop": shop,
        "bank_details": bank_details,
        "active_tab": "banking"
    })


@router.post("/bank")
async def update_bank_details(
    request: Request,
    account_holder: str = Form(...),
    bank_name: str = Form(...),
    account_number: str = Form(...),
    confirm_account_number: str = Form(...),
    ifsc: Optional[str] = Form(None),
    branch_name: Optional[str] = Form(None),
    upi_id: Optional[str] = Form(None),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate & save bank details (encrypted account number)."""
    try:
        shop = getattr(user, "shop", None)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop not found")

        if account_number != confirm_account_number:
            raise HTTPException(status_code=400, detail="Account numbers do not match")

        if ifsc and not validation_service.validate_ifsc(ifsc):
            raise HTTPException(status_code=400, detail="Invalid IFSC code format")
        if upi_id and not validation_service.validate_upi(upi_id):
            raise HTTPException(status_code=400, detail="Invalid UPI ID format")

        # Check if account number is masked (starts with ****)
        is_masked_input = account_number.strip().startswith("****")
        
        bank_details = db.query(models.BankDetail).filter(
            models.BankDetail.shop_id == shop.id
        ).first()

        if bank_details:
            bank_details.account_holder = account_holder
            bank_details.bank_name = bank_name
            
            # Only update account number if it's NOT the masked version
            if not is_masked_input:
                bank_details.account_number_encrypted = encryption_service.encrypt_account_number(account_number)
                
            bank_details.ifsc = ifsc
            bank_details.branch_name = branch_name
            bank_details.upi_id = upi_id
            bank_details.updated_at = datetime.utcnow()
        else:
            # New record - must have real account number
            if is_masked_input:
                 raise HTTPException(status_code=400, detail="Cannot save masked account number for new record")
                 
            bank_details = models.BankDetail(
                shop_id=shop.id,
                account_holder=account_holder,
                bank_name=bank_name,
                account_number_encrypted=encryption_service.encrypt_account_number(account_number),
                ifsc=ifsc,
                branch_name=branch_name,
                upi_id=upi_id
            )
            db.add(bank_details)

        db.commit()
        db.refresh(bank_details)

        return RedirectResponse(url="/settings/bank?success=Bank details updated successfully", status_code=303)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating bank details: {str(e)}")


@router.post("/bank/qr")
async def upload_qr_code(
    qr_code: UploadFile = File(...),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload UPI QR code using storage abstraction."""
    try:
        shop = getattr(user, "shop", None)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop not found")

        # Save using storage abstraction
        qr_web_path = save_upload_file(qr_code, "qr_codes", f"shop_{shop.id}")

        bank_details = db.query(models.BankDetail).filter(
            models.BankDetail.shop_id == shop.id
        ).first()

        if not bank_details:
            raise HTTPException(status_code=404, detail="Bank details not found. Please add bank details first.")

        bank_details.qr_code_path = qr_web_path
        bank_details.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(bank_details)

        return JSONResponse({"success": True, "qr_code_path": qr_web_path})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading QR code: {str(e)}")


# ========== SECURITY ENDPOINTS ==========
@router.get("/security", response_class=HTMLResponse)
async def get_security(
    request: Request,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Render Security tab."""
    return templates.TemplateResponse("settings/security.html", {
        "request": request,
        "user": user,
        "active_tab": "security"
    })

@router.post("/security/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password with basic checks."""
    try:
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="New passwords do not match")
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

        return JSONResponse({"success": True, "message": "Password changed successfully"})
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error changing password: {str(e)}")


@router.post("/security/logout-all")
async def logout_all_sessions(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke all API tokens for the user (logout everywhere)."""
    try:
        db.query(models.APIToken).filter(
            models.APIToken.user_id == user.id,
            models.APIToken.revoked == False
        ).update({"revoked": True})
        db.commit()
        return JSONResponse({"success": True, "message": "Logged out from all devices"})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error logging out: {str(e)}")


# ========== NOTIFICATIONS ENDPOINTS ==========
@router.get("/notifications", response_class=HTMLResponse)
async def get_notifications(
    request: Request,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get or create default notification preferences and render page."""
    notif_prefs = db.query(models.NotificationPreference).filter(
        models.NotificationPreference.user_id == user.id
    ).first()

    if not notif_prefs:
        notif_prefs = models.NotificationPreference(
            user_id=user.id,
            invoice_email=True,
            invoice_whatsapp=False,
            monthly_gst_summary=True,
            payment_alerts=True
        )
        db.add(notif_prefs)
        db.commit()
        db.refresh(notif_prefs)

    return templates.TemplateResponse("settings/notifications.html", {
        "request": request,
        "user": user,
        "preferences": notif_prefs,
        "active_tab": "notifications"
    })


@router.post("/notifications")
async def update_notifications(
    invoice_email: Optional[str] = Form(None),
    invoice_whatsapp: Optional[str] = Form(None),
    monthly_gst_summary: Optional[str] = Form(None),
    payment_alerts: Optional[str] = Form(None),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences (checkbox parsing)."""
    try:
        invoice_email_b = _parse_bool_from_form(invoice_email)
        invoice_whatsapp_b = _parse_bool_from_form(invoice_whatsapp)
        monthly_gst_summary_b = _parse_bool_from_form(monthly_gst_summary)
        payment_alerts_b = _parse_bool_from_form(payment_alerts)

        notif_prefs = db.query(models.NotificationPreference).filter(
            models.NotificationPreference.user_id == user.id
        ).first()

        if not notif_prefs:
            notif_prefs = models.NotificationPreference(user_id=user.id)
            db.add(notif_prefs)

        notif_prefs.invoice_email = invoice_email_b
        notif_prefs.invoice_whatsapp = invoice_whatsapp_b
        notif_prefs.monthly_gst_summary = monthly_gst_summary_b
        notif_prefs.payment_alerts = payment_alerts_b

        db.commit()
        db.refresh(notif_prefs)

        return RedirectResponse(url="/settings/notifications?success=Notification preferences updated", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating notifications: {str(e)}")


# ========== BILLING (SKELETON) ==========
@router.get("/billing", response_class=HTMLResponse)
async def get_billing(
    request: Request,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Skeleton billing page for future work."""
    return templates.TemplateResponse("settings/billing.html", {
        "request": request,
        "user": user,
        "active_tab": "billing",
        "current_plan": "Free Trial",
        "renewal_date": None
    })
