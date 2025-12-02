from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.dependencies import get_current_shop, get_current_user
from app import models
from datetime import date, timedelta

router = APIRouter(tags=["reports"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/reports/gst-summary")
def gst_summary(
    request: Request,
    start_date: date = Query(default=date.today().replace(day=1)),
    end_date: date = Query(default=date.today()),
    user: models.User = Depends(get_current_user),
    shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    invoices = db.query(models.Invoice).filter(
        models.Invoice.shop_id == shop.id,
        models.Invoice.date >= start_date,
        models.Invoice.date <= end_date
    ).all()
    
    total_taxable = sum(inv.taxable_amount for inv in invoices)
    total_cgst = sum(inv.cgst_amount for inv in invoices)
    total_sgst = sum(inv.sgst_amount for inv in invoices)
    total_igst = sum(inv.igst_amount for inv in invoices)
    total_tax = total_cgst + total_sgst + total_igst
    
    return templates.TemplateResponse("reports/gst_summary.html", {
        "request": request,
        "user": user,
        "start_date": start_date,
        "end_date": end_date,
        "total_taxable": total_taxable,
        "total_cgst": total_cgst,
        "total_sgst": total_sgst,
        "total_igst": total_igst,
        "total_tax": total_tax,
        "title": "GST Summary"
    })

@router.get("/reports/ledger")
def customer_ledger(
    request: Request,
    customer_id: int = Query(None),
    start_date: date = Query(default=date.today().replace(day=1)),
    end_date: date = Query(default=date.today()),
    user: models.User = Depends(get_current_user),
    shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    customers = db.query(models.Customer).filter(models.Customer.shop_id == shop.id).all()
    
    ledger_entries = []
    customer = None
    opening_balance = 0
    closing_balance = 0
    
    if customer_id:
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        if customer:
            # Calculate opening balance before start_date
            # This is simplified. In real app, need to sum all previous invoices/payments.
            # For now, we just take customer opening balance + invoices before start_date
            
            prev_invoices = db.query(func.sum(models.Invoice.grand_total)).filter(
                models.Invoice.customer_id == customer_id,
                models.Invoice.date < start_date
            ).scalar() or 0
            
            opening_balance = customer.opening_balance + prev_invoices
            
            # Get invoices in range
            invoices = db.query(models.Invoice).filter(
                models.Invoice.customer_id == customer_id,
                models.Invoice.date >= start_date,
                models.Invoice.date <= end_date
            ).order_by(models.Invoice.date).all()
            
            running_balance = opening_balance
            for inv in invoices:
                running_balance += inv.grand_total
                ledger_entries.append({
                    "date": inv.date,
                    "particulars": f"Invoice #{inv.invoice_no}",
                    "debit": inv.grand_total,
                    "credit": 0,
                    "balance": running_balance
                })
            
            closing_balance = running_balance

    return templates.TemplateResponse("reports/customer_ledger.html", {
        "request": request,
        "user": user,
        "customers": customers,
        "selected_customer_id": customer_id,
        "customer": customer,
        "start_date": start_date,
        "end_date": end_date,
        "ledger_entries": ledger_entries,
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "title": "Customer Ledger"
    })
