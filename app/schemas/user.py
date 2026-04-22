from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Registration and login
class UserCreate(BaseModel):
    """ Used as the body for POST /auth/register and POST /auth/login """
    email: EmailStr = Field(..., title="User email", description="Valid email address of the user")
    password: str = Field(..., title="User password", description="Plain text password provided by the user")

# Refresh token
class RefreshRequest(BaseModel):
    """ Used as the body for POST /auth/refresh """
    refresh_token: str = Field(..., title="Refresh token", description="JWT refresh token used to obtain a new access token")

# User data
class UserResponse(BaseModel):
    """ Used at response_model """
    id: int = Field(..., title="User ID", description="Unique identifier of the user")
    email: EmailStr = Field(..., title="User email", description="User's email address")
    is_active: bool = Field(..., title="Active status", description="Indicates whether the user account is active")
    created_at: datetime = Field(..., title="Creation timestamp", description="Date and time when the user was created")

    model_config = {"from_attributes": True}