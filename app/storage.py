"""
Storage abstraction layer for handling file uploads.
Supports both local filesystem (development) and S3-compatible storage (production).
"""
import os
import boto3
from pathlib import Path
from typing import BinaryIO, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class StorageProvider:
    """Base storage provider interface"""
    
    def save(self, file: BinaryIO, path: str) -> str:
        """Save file and return the accessible URL/path"""
        raise NotImplementedError
    
    def get_url(self, path: str) -> str:
        """Get the URL for accessing a stored file"""
        raise NotImplementedError
    
    def delete(self, path: str) -> bool:
        """Delete a file"""
        raise NotImplementedError
    
    def exists(self, path: str) -> bool:
        """Check if file exists"""
        raise NotImplementedError


class LocalStorage(StorageProvider):
    """Local filesystem storage for development"""
    
    def __init__(self, base_path: str = "app/static/uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, file: BinaryIO, path: str) -> str:
        """Save file to local filesystem"""
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'wb') as f:
            content = file.read()
            f.write(content)
        
        # Return web-accessible path
        return f"/static/uploads/{path}"
    
    def get_url(self, path: str) -> str:
        """Get URL for local file"""
        # Remove /static/uploads/ prefix if present
        clean_path = path.replace("/static/uploads/", "")
        return f"/static/uploads/{clean_path}"
    
    def delete(self, path: str) -> bool:
        """Delete file from local filesystem"""
        try:
            full_path = self.base_path / path.replace("/static/uploads/", "")
            if full_path.exists():
                full_path.unlink()
                return True
        except Exception as e:
            logger.error(f"Error deleting file {path}: {e}")
        return False
    
    def exists(self, path: str) -> bool:
        """Check if file exists locally"""
        full_path = self.base_path / path.replace("/static/uploads/", "")
        return full_path.exists()


class S3Storage(StorageProvider):
    """S3-compatible storage for production"""
    
    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self.region = settings.S3_REGION
        
        # Initialize S3 client
        s3_config = {
            'region_name': self.region,
        }
        
        # Add credentials if provided
        if settings.S3_ACCESS_KEY_ID and settings.S3_SECRET_ACCESS_KEY:
            s3_config['aws_access_key_id'] = settings.S3_ACCESS_KEY_ID
            s3_config['aws_secret_access_key'] = settings.S3_SECRET_ACCESS_KEY
        
        # Add custom endpoint for R2, MinIO, etc.
        if settings.S3_ENDPOINT_URL:
            s3_config['endpoint_url'] = settings.S3_ENDPOINT_URL
        
        self.s3_client = boto3.client('s3', **s3_config)
    
    def save(self, file: BinaryIO, path: str) -> str:
        """Upload file to S3"""
        try:
            # Upload file
            self.s3_client.upload_fileobj(
                file,
                self.bucket,
                path,
                ExtraArgs={'ACL': 'public-read'}  # Make file publicly accessible
            )
            
            # Return URL
            return self.get_url(path)
        
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}")
            raise
    
    def get_url(self, path: str) -> str:
        """Get public URL for S3 object"""
        if settings.S3_ENDPOINT_URL:
            # Custom endpoint (R2, MinIO, etc.)
            base_url = settings.S3_ENDPOINT_URL.rstrip('/')
            return f"{base_url}/{self.bucket}/{path}"
        else:
            # Standard AWS S3 URL
            return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{path}"
    
    def delete(self, path: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=path)
            return True
        except Exception as e:
            logger.error(f"Error deleting from S3 {path}: {e}")
            return False
    
    def exists(self, path: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=path)
            return True
        except:
            return False


# Storage factory
def get_storage() -> StorageProvider:
    """Get the appropriate storage provider based on configuration"""
    if settings.STORAGE_PROVIDER.lower() == "s3":
        return S3Storage()
    else:
        return LocalStorage(settings.UPLOADS_PATH)


# Convenience functions
storage = get_storage()


def save_upload(file: BinaryIO, path: str) -> str:
    """
    Save uploaded file and return its URL.
    
    Args:
        file: File object to save
        path: Relative path where file should be saved (e.g., "logos/shop_logo.png")
    
    Returns:
        URL or path where file can be accessed
    """
    return storage.save(file, path)


def get_file_url(path: str) -> str:
    """
    Get URL for accessing a stored file.
    
    Args:
        path: File path or existing URL
    
    Returns:
        Accessible URL for the file
    """
    # If it's already a full URL or /static path, return as-is
    if path.startswith(('http://', 'https://', '/static/')):
        return path
    
    return storage.get_url(path)


def delete_file(path: str) -> bool:
    """
    Delete a stored file.
    
    Args:
        path: File path to delete
    
    Returns:
        True if deleted successfully
    """
    return storage.delete(path)


def file_exists(path: str) -> bool:
    """
    Check if a file exists in storage.
    
    Args:
        path: File path to check
    
    Returns:
        True if file exists
    """
    return storage.exists(path)
