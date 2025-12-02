from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from datetime import datetime, timedelta

# Cache configuration for static files
class CachedStaticFiles(StaticFiles):
    def __init__(self, *args, **kwargs):
        self.cache_max_age = kwargs.pop('cache_max_age', 31536000)  # 1 year default
        super().__init__(*args, **kwargs)
    
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        
        # Add cache headers for static files
        if isinstance(response, Response):
            # Cache images, fonts, and CSS/JS for 1 year
            if any(path.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp', '.woff', '.woff2', '.css', '.js']):
                response.headers['Cache-Control'] = f'public, max-age={self.cache_max_age}, immutable'
            # Cache other static files for 1 week
            else:
                response.headers['Cache-Control'] = 'public, max-age=604800'
        
        return response
