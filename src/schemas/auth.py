"""
This module defines Pydantic models for handling access tokens, refresh tokens, and email requests.

Models:
- AccessTokenRefreshResponse: Represents the response containing refreshed access and refresh tokens.
- AccessTokenResponse: Represents the response containing an access token.
- RequestEmail: Represents the request body for requesting an email.

"""

from datetime import datetime

from pydantic import BaseModel, EmailStr

class AccessTokenRefreshResponse(BaseModel):
    """
    Represents the response containing refreshed access and refresh tokens.

    Attributes:
    - token_type (str): The type of token (default: "bearer").
    - access_token (str): The new access token.
    - expire_access_token (datetime): The expiration date and time of the access token.
    - refresh_token (str): The new refresh token.
    - expire_refresh_token (datetime): The expiration date and time of the refresh token.

    """
    token_type: str = "bearer"
    access_token: str
    expire_access_token: datetime
    refresh_token: str
    expire_refresh_token: datetime


class AccessTokenResponse(BaseModel):
    """
    Represents the response containing an access token.

    Attributes:
    - access_token (str): The access token.
    - token_type (str): The type of token (default: "bearer").

    """

    access_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Represents the request body for requesting an email.

    Attributes:
    - email (EmailStr): The email address to be requested.

    """

    email: EmailStr
