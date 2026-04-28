from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.limiter import limiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
from app.core.dependencies import get_db, get_current_user
from app.core.security import (verify_password, create_access_token, create_refresh_token, decode_token)
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, RefreshRequest
from app.schemas.token import Token
from app.main import limiter

# Authentication
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """ User login - max 5 requests per minute per IP """
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    # Generic message
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credential")

    return Token(access_token=create_access_token(user.email), refresh_token=create_refresh_token(user.email))


@router.post("/refresh", response_model=Token)
async def refresh(payload: RefreshRequest):
    """ Renew tokens using the refresh token """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        data = decode_token(payload.refresh_token)
        # Verify that it is a refresh token, not an access token
        if data.get("type") != "refresh":
            raise credentials_exception
        email: str = data.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return Token(
        access_token=create_access_token(email),
        refresh_token=create_refresh_token(email),
    )

@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """ Returns authenticated user data """
    return current_user