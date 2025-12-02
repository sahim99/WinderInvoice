from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.dependencies import get_current_user, get_current_shop
from app.database import get_db
from app import models
from datetime import datetime, timedelta

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def homepage(request: Request):
    """Public homepage - no authentication required"""
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/home-teal")
def homepage_teal(request: Request):
    """Teal theme homepage"""
    return templates.TemplateResponse("home_teal.html", {"request": request})

@router.get("/home-blue")
def homepage_blue(request: Request):
    """Blue theme homepage"""
    return templates.TemplateResponse("home_blue.html", {"request": request})

@router.get("/home-dark")
def homepage_dark(request: Request):
    """Dark theme homepage"""
    return templates.TemplateResponse("home_dark.html", {"request": request})

@router.get("/home-dark-neon")
def homepage_dark_neon(request: Request):
    """Neon Dark theme homepage"""
    return templates.TemplateResponse("home_dark_neon.html", {"request": request})

@router.get("/home-dark-minimal")
def homepage_dark_minimal(request: Request):
    """Minimal Dark theme homepage"""
    return templates.TemplateResponse("home_dark_minimal.html", {"request": request})

@router.get("/home-modern")
def homepage_modern(request: Request):
    """Modern Dark theme homepage"""
    return templates.TemplateResponse("home_modern.html", {"request": request})

@router.get("/home-elegant")
def homepage_elegant(request: Request):
    """Elegant Dark theme homepage"""
    return templates.TemplateResponse("home_elegant.html", {"request": request})

@router.get("/home-v2")
def homepage_v2(request: Request):
    """Redesigned Homepage V2"""
    return templates.TemplateResponse("home_v2.html", {"request": request})


def get_dashboard_data(db: Session, shop: models.Shop):
    # Get counts
    total_customers = db.query(models.Customer).filter(models.Customer.shop_id == shop.id).count()
    total_invoices = db.query(models.Invoice).filter(models.Invoice.shop_id == shop.id).count()
    total_products = db.query(models.Product).filter(models.Product.shop_id == shop.id).count()
    
    # Get revenue totals
    total_revenue = db.query(func.sum(models.Invoice.grand_total)).filter(
        models.Invoice.shop_id == shop.id
    ).scalar() or 0
    
    # Get this month's revenue
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_revenue = db.query(func.sum(models.Invoice.grand_total)).filter(
        models.Invoice.shop_id == shop.id,
        extract('month', models.Invoice.date) == current_month,
        extract('year', models.Invoice.date) == current_year
    ).scalar() or 0
    
    # Get recent invoices (last 5)
    recent_invoices = db.query(models.Invoice).filter(
        models.Invoice.shop_id == shop.id
    ).order_by(models.Invoice.date.desc()).limit(5).all()
    
    # Get GST summary
    total_cgst = db.query(func.sum(models.Invoice.cgst_amount)).filter(
        models.Invoice.shop_id == shop.id
    ).scalar() or 0
    
    total_sgst = db.query(func.sum(models.Invoice.sgst_amount)).filter(
        models.Invoice.shop_id == shop.id
    ).scalar() or 0
    
    total_igst = db.query(func.sum(models.Invoice.igst_amount)).filter(
        models.Invoice.shop_id == shop.id
    ).scalar() or 0
    
    
    # Chart Data: Monthly Revenue (Last 6 months)
    today = datetime.now()
    chart_labels = []
    chart_revenue = []
    
    for i in range(5, -1, -1):
        date = today - timedelta(days=i*30) # Approx month
        month_name = date.strftime("%b")
        chart_labels.append(month_name)
        
        # Calculate revenue for this specific month/year
        rev = db.query(func.sum(models.Invoice.grand_total)).filter(
            models.Invoice.shop_id == shop.id,
            extract('month', models.Invoice.date) == date.month,
            extract('year', models.Invoice.date) == date.year
        ).scalar() or 0
        chart_revenue.append(rev)

    return {
        "total_customers": total_customers,
        "total_invoices": total_invoices,
        "total_products": total_products,
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "recent_invoices": recent_invoices,
        "total_cgst": total_cgst,
        "total_sgst": total_sgst,
        "total_igst": total_igst,
        "chart_labels": chart_labels,
        "chart_revenue": chart_revenue,
    }

@router.get("/dashboard")
def dashboard(
    request: Request, 
    current_user: models.User = Depends(get_current_user),
    shop: models.Shop = Depends(get_current_shop),
    db: Session = Depends(get_db)
):
    """Ultimate Dashboard - Default View"""
    data = get_dashboard_data(db, shop)
    return templates.TemplateResponse("dashboard_ultimate.html", {
        "request": request, 
        "user": current_user,
        "title": "Business Overview",
        **data
    })
