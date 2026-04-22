from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth, article

# Models
import app.models.user
import app.models.article

# FastAPI
main = FastAPI(
    title=settings.app_name,
    # Swagger UI avaible on /docs
)

# Router registration
main.include_router(auth.router)
main.include_router(article.router)

# Health check
@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}
