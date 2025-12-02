import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gst_billing.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Storage Configuration
    STORAGE_PROVIDER: str = os.getenv("STORAGE_PROVIDER", "local")  # "local" or "s3"
    
    # S3/Object Storage (for production file uploads)
    S3_BUCKET: str = os.getenv("S3_BUCKET", "")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    S3_ACCESS_KEY_ID: str = os.getenv("S3_ACCESS_KEY_ID", "")
    S3_SECRET_ACCESS_KEY: str = os.getenv("S3_SECRET_ACCESS_KEY", "")
    S3_ENDPOINT_URL: str = os.getenv("S3_ENDPOINT_URL", "")  # For R2, MinIO, etc.
    
    # PDF Generation
    PDF_ENGINE: str = os.getenv("PDF_ENGINE", "xhtml2pdf")  # "xhtml2pdf", "chromium", "wkhtmltopdf"
    
    # File Paths
    UPLOADS_PATH: str = os.getenv("UPLOADS_PATH", "app/static/uploads")
    DEFAULT_PLACEHOLDER_QR: str = os.getenv("DEFAULT_PLACEHOLDER_QR", "/static/img/qr_placeholder.png")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
