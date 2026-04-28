from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth, article

# FastAPI
main = FastAPI(
    title=settings.app_name or "",
    description=settings.description or "",
    version=settings.version or "1.0.0"
    # Swagger UI avaible on /docs
)

# Router registration
main.include_router(auth.router)
main.include_router(article.router)

# Health check
@main.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}
