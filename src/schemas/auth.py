from datetime import datetime

from pydantic import BaseModel, EmailStr

class AccessTokenRefreshResponse(BaseModel):
    token_type: str = "bearer"
    access_token: str
    expire_access_token: datetime
    refresh_token: str
    expire_refresh_token: datetime

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    email: EmailStr
