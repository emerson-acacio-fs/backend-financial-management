from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.router import api_router
from app.core.config import settings
from app.core.errors import install_exception_handlers

app = FastAPI(title=settings.app_name)
install_exception_handlers(app)

app.include_router(health_router)
app.include_router(api_router, prefix=settings.api_prefix)
