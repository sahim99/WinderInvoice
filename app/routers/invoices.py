from fastapi import APIRouter, Depends, Request, Form, status, HTTPException
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_shop, get_current_user
from app import models, schemas
from app.services import invoice_service
from typing import List, Optional
from datetime import date
import json
from xhtml2pdf import pisa
from io import BytesIO
import re

router = APIRouter(tags=["invoices"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/invoices")
def list_invoices(request: Request, user: models.User = Depends(get_current_user), shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    invoices = db.query(models.Invoice).filter(models.Invoice.shop_id == shop.id).order_by(models.Invoice.date.desc()).all()
    return templates.TemplateResponse("invoices/list.html", {"request": request, "user": user, "invoices": invoices, "title": "Invoices"})

@router.get("/invoices/new")
def new_invoice(request: Request, user: models.User = Depends(get_current_user), shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    customers = db.query(models.Customer).filter(models.Customer.shop_id == shop.id).all()
    products = db.query(models.Product).filter(models.Product.shop_id == shop.id).all()
    next_invoice_no = invoice_service.generate_invoice_number(shop.id, db)
    return templates.TemplateResponse("invoices/create.html", {
        "request": request,
        "user": user,
        "customers": customers, 
        "products": products,
        "next_invoice_no": next_invoice_no,
        "today": date.today(),
        "title": "New Invoice"
    })

@router.post("/invoices/new")
async def create_invoice(
    request: Request,
    customer_id: int = Form(...),
    invoice_no: str = Form(...),
    date_str: str = Form(..., alias="date"),
    place_of_supply: str = Form(...),
    vehicle_no: Optional[str] = Form(None),
    eway_bill_no: Optional[str] = Form(None),
    items_json: str = Form(...), # Receive items as JSON string
    shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    try:
        items_data = json.loads(items_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid items data")

    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Determine if inter-state
    # Logic: Prefer state_code comparison if available, otherwise fallback to normalized state names
    def normalize(s):
        return (str(s) or '').strip().lower()

    c_state_code = getattr(customer, 'state_code', None)
    s_state_code = getattr(shop, 'state_code', None)
    
    # If both have state codes, compare them
    if c_state_code and s_state_code:
        is_inter_state = normalize(c_state_code) != normalize(s_state_code)
    else:
        # Fallback to state names
        c_state = getattr(customer, 'state', '')
        s_state = getattr(shop, 'state', '')
        is_inter_state = normalize(c_state) != normalize(s_state)

    # Create Invoice
    invoice = models.Invoice(
        shop_id=shop.id,
        customer_id=customer_id,
        invoice_no=invoice_no,
        date=date.fromisoformat(date_str),
        place_of_supply=place_of_supply,
        vehicle_no=vehicle_no,
        eway_bill_no=eway_bill_no,
        status="Generated"
    )
    db.add(invoice)
    db.flush() # Get ID

    total_taxable = 0
    total_cgst = 0
    total_sgst = 0
    total_igst = 0
    grand_total = 0

    for item in items_data:
        qty = float(item['qty'])
        rate = float(item['rate'])
        tax_rate = float(item['tax_rate'])
        
        no_of_pkts = int(item.get('no_of_pkts', 0))
        
        taxable_value = qty * rate
        total_tax_amount = taxable_value * (tax_rate / 100)
        
        if is_inter_state:
            igst_amount = total_tax_amount
            cgst_amount = 0.0
            sgst_amount = 0.0
        else:
            cgst_amount = total_tax_amount / 2.0
            sgst_amount = total_tax_amount / 2.0
            igst_amount = 0.0
        
        item_total = taxable_value + total_tax_amount
        
        invoice_item = models.InvoiceItem(
            invoice_id=invoice.id,
            product_id=item.get('product_id'), # Optional if manual
            description=item['description'],
            hsn_code=item['hsn_code'],
            no_of_pkts=no_of_pkts,
            qty=qty,
            unit=item['unit'],
            rate=rate,
            taxable_value=taxable_value,
            tax_rate=tax_rate,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            igst_amount=igst_amount,
            total_amount=item_total
        )
        db.add(invoice_item)
        
        total_taxable += taxable_value
        total_cgst += cgst_amount
        total_sgst += sgst_amount
        total_igst += igst_amount
        grand_total += item_total

        # Update Product Stock (Unit)
        if item.get('product_id'):
            product = db.query(models.Product).filter(models.Product.id == item['product_id']).first()
            if product:
                try:
                    # Attempt to parse current stock (unit) as float
                    current_stock = float(product.unit) if product.unit else 0.0
                    new_stock = current_stock - qty
                    # Update product unit, keeping it as a string since the column is String
                    product.unit = str(int(new_stock)) if new_stock.is_integer() else str(new_stock)
                    db.add(product)
                except ValueError:
                    # product.unit might not be a number (e.g., "10 pcs"), skip auto-update or handle differently
                    print(f"Skipping stock update for product {product.id}: 'unit' ({product.unit}) is not a number.")

    # Update invoice totals
    invoice.taxable_amount = total_taxable
    invoice.cgst_amount = total_cgst
    invoice.sgst_amount = total_sgst
    invoice.igst_amount = total_igst
    
    # Round off
    rounded_total = round(grand_total)
    invoice.round_off = rounded_total - grand_total
    invoice.grand_total = rounded_total
    invoice.amount_in_words = invoice_service.num_to_words(rounded_total)
    
    db.commit()
    
    return RedirectResponse(url=f"/invoices/{invoice.id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/invoices/{invoice_id}")
def view_invoice(invoice_id: int, request: Request, user: models.User = Depends(get_current_user), shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id, models.Invoice.shop_id == shop.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    customer = db.query(models.Customer).filter(models.Customer.id == invoice.customer_id).first()
    
    # Calculate totals for template
    taxable_amount = invoice.taxable_amount
    cgst_amount = invoice.cgst_amount
    sgst_amount = invoice.sgst_amount
    igst_amount = invoice.igst_amount
    total_amount = invoice.grand_total
    # Normalize for comparison
    def normalize(s):
        return (str(s) or '').strip().lower()
    
    is_intrastate = normalize(shop.state) == normalize(customer.state)
    amount_in_words = invoice.amount_in_words
    
    # Fetch bank details if available
    bank_name = ""
    account_number = ""
    ifsc_code = ""
    qr_code_path = getattr(shop, "qr_code_path", None)
    
    if shop.bank_details and len(shop.bank_details) > 0:
        bank = shop.bank_details[0]
        bank_name = bank.bank_name
        ifsc_code = bank.ifsc
        # Decrypt account number
        from app.services.encryption_service import decrypt_account_number
        try:
            account_number = decrypt_account_number(bank.account_number_encrypted)
        except Exception:
            account_number = "****"
            
        # Use bank QR if shop QR is missing
        if not qr_code_path and bank.qr_code_path:
            qr_code_path = bank.qr_code_path

    # Construct shop_data dict to match PDF template expectations
    shop_data = {
        "name": getattr(shop, "name", "") or "",
        "address": getattr(shop, "address_line1", "") or "",
        "city": getattr(shop, "city", "") or "",
        "state": getattr(shop, "state", "") or "",
        "state_code": getattr(shop, "state", "") or "", # Fallback to state name as code is removed
        "pincode": getattr(shop, "pincode", "") or "",
        "phone": getattr(shop, "business_phone", "") or "",
        "email": getattr(shop, "business_email", "") or "",
        "gstin": getattr(shop, "gstin", "") or "",
        "bank_name": bank_name,
        "account_number": account_number,
        "ifsc_code": ifsc_code,
        "branch_name": getattr(shop, "branch_name", "") or getattr(shop, "address_line1", "") or "", # Fallback to address if branch name missing
        "logo_path": getattr(shop, "logo_path", "/static/img/logo-w-gradient-new.png"),
        "qr_code_path": qr_code_path,
    }
    
    return templates.TemplateResponse("invoices/print.html", {
        "request": request,
        "user": user,
        "invoice": invoice, 
        "shop": shop_data, 
        "customer": customer,
        "consignee": customer, # Default to customer for now, or fetch if you have a consignee model
        "taxable_amount": taxable_amount,
        "cgst_amount": cgst_amount,
        "sgst_amount": sgst_amount,
        "igst_amount": igst_amount,
        "total_amount": total_amount,
        "is_intrastate": is_intrastate,
        "amount_in_words": amount_in_words,
        "freight": 0.0 # Default freight
    })

@router.get("/invoices/{invoice_id}/pdf")
def download_invoice_pdf(invoice_id: int, shop: models.Shop = Depends(get_current_shop), db: Session = Depends(get_db)):
    """Generate and download invoice as PDF"""
    print(f"DEBUG: PDF Route Hit. User: {db.query(models.User).filter(models.User.shop_id == shop.id).first().email if shop else 'Unknown'}")
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id, models.Invoice.shop_id == shop.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    customer = db.query(models.Customer).filter(models.Customer.id == invoice.customer_id).first()
    
    # Calculate totals for template
    taxable_amount = invoice.taxable_amount
    cgst_amount = invoice.cgst_amount
    sgst_amount = invoice.sgst_amount
    igst_amount = invoice.igst_amount
    total_amount = invoice.grand_total
    # Normalize for comparison
    def normalize(s):
        return (str(s) or '').strip().lower()

    is_intrastate = normalize(getattr(shop, 'state', '')) == normalize(getattr(customer, 'state', ''))
    amount_in_words = invoice.amount_in_words
    
    # Safe extract shop data to dict to prevent AttributeError on missing fields
    # Fetch bank details if available
    bank_name = ""
    account_number = ""
    ifsc_code = ""
    qr_code_path = getattr(shop, "qr_code_path", None)
    
    if shop.bank_details and len(shop.bank_details) > 0:
        bank = shop.bank_details[0]
        bank_name = bank.bank_name
        ifsc_code = bank.ifsc
        # Decrypt account number
        from app.services.encryption_service import decrypt_account_number
        try:
            account_number = decrypt_account_number(bank.account_number_encrypted)
        except Exception:
            account_number = "****"
            
        # Use bank QR if shop QR is missing
        if not qr_code_path and bank.qr_code_path:
            qr_code_path = bank.qr_code_path

    shop_data = {
        "name": getattr(shop, "name", "") or "",
        "address": getattr(shop, "address_line1", "") or "",
        "city": getattr(shop, "city", "") or "",
        "state": getattr(shop, "state", "") or "",
        "state_code": getattr(shop, "state", "") or "", # Fallback to state name as code is removed
        "pincode": getattr(shop, "pincode", "") or "",
        "phone": getattr(shop, "business_phone", "") or "",
        "email": getattr(shop, "business_email", "") or "",
        "gstin": getattr(shop, "gstin", "") or "",
        "bank_name": bank_name,
        "account_number": account_number,
        "ifsc_code": ifsc_code,
        "branch_name": getattr(shop, "branch_name", "") or getattr(shop, "address_line1", "") or "", # Fallback to address if branch name missing
        "logo_path": getattr(shop, "logo_path", "/static/img/logo-w-gradient-new.png"),
        "qr_code_path": qr_code_path,
    }
    
    # Render HTML template using simplified PDF template
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('app/templates'))
    template = env.get_template('invoices/print_pdf.html')
    
    html_content = template.render(
        invoice=invoice,
        shop=shop_data,
        customer=customer,
        consignee=customer, # Default consignee
        taxable_amount=taxable_amount,
        cgst_amount=cgst_amount,
        sgst_amount=sgst_amount,
        igst_amount=igst_amount,
        total_amount=total_amount,
        is_intrastate=is_intrastate,
        amount_in_words=amount_in_words,
        freight=0.0 # Default freight
    )
    
    # Define link_callback to resolve static files (CSS/Images)
    def link_callback(uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
        """
        import os
        
        # Handle static files
        if uri.startswith('/static/'):
            # Remove leading slash and join with current working directory
            path = os.path.join(os.getcwd(), 'app', uri.lstrip('/'))
        else:
            path = uri
            
        # Make sure file exists
        if not os.path.isfile(path):
            print(f"PDF GENERATION WARNING: Missing file {path}")
            return uri
            
        return path

    # Generate PDF using xhtml2pdf with link_callback
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer, link_callback=link_callback)
    
    if pisa_status.err:
        raise HTTPException(status_code=500, detail="Error generating PDF")
    
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()
    
    # Create safe filename: INV-0001-CustomerName.pdf
    raw_name = f"INV-{invoice.invoice_no}-{customer.name}"
    # Remove unsafe characters for filenames
    safe_name = re.sub(r'[^A-Za-z0-9._-]+', '-', raw_name)
    filename = f"{safe_name}.pdf"
    
    # Return PDF as download with proper Content-Disposition header
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
