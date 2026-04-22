from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.models.user import User

# Security schema
bearer_scheme = HTTPBearer()

# DB session
async def get_db():
    """ Provides a database session for each request """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Authenticated user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """ Verifies the JWT and returns the authenticated user """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or invalid", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_token(credentials.credentials)
        # Check the token type
        if payload.get("type") != "access":
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Create user in DB
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active or not user.is_admin:
        raise credentials_exception

    return user