from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import HTTPException
import logging
import traceback

from app.database import engine, Base
from app.config import settings

# Create tables (for local dev, normally use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GST Billing App")

logging.basicConfig(filename='app.log', level=logging.ERROR)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    logging.error(f"Global error: {error_msg}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        # Check if the request expects HTML or is a PDF download
        accept = request.headers.get("accept", "")
        if "text/html" in accept or request.url.path.endswith("/pdf"):
            return RedirectResponse(url="/auth/login", status_code=302)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.get("/demo")
async def demo_redirect():
    return RedirectResponse(url="/auth/demo")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Make config available to all templates globally
templates.env.globals['config'] = settings

# Include routers
from app.routers import auth, dashboard, masters, invoices, reports, settings

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(masters.router)
app.include_router(invoices.router)
app.include_router(reports.router)
app.include_router(settings.router)
