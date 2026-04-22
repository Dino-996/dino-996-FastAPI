from pydantic import BaseModel, Field

class Token(BaseModel):
    """ Login and refresh response """
    access_token: str = Field(default=..., title="Access token", description="JWT used to authenticate API requests")
    refresh_token: str = Field(default=..., title="Refresh token", description="Long-lived token used to obtain a new access token when the current one expires")
    token_type: str = Field(default="bearer", title="Type of token", description="Type of token. Typically 'bearer', used in the Authorization header scheme", examples=["bearer", "bearer-auth"])
