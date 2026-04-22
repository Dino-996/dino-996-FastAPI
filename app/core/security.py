from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from typing import Any

# Password hashing with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """ Transforms a cleartext password into an irreversible hash """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ Compare a cleartext password with its hash stored in the DB """
    return pwd_context.verify(plain_password, hashed_password)

# JWT (JSON Web Token) Generation
def create_access_token(subject: str) -> str:
    """ Create an access token with a short expiration date """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, str | datetime] = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(subject: str) -> str:
    """ Create a refresh token with a long expiration (7 days by default) """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, str | datetime] = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def decode_token(token: str) -> dict[str, Any]:
    """ Decode and verify a JWT """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])