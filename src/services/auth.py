from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from pydantic_settings import BaseSettings
from config.config import settings
from db.database import get_db
from db.models import User
from .auth_token import AuthToken
from repository import users as repository_users
from schemas.auth import AccessTokenRefreshResponse


class Auth(AuthToken):
    """
    Class for managing authentication and authorization tokens.

    Parameters:
    - secret_key (str): The secret key used for encoding and decoding tokens.
    - algorithm (str, optional): The algorithm used for encoding tokens. Defaults to None.
    - token_url (str, optional): The URL for token authentication. Defaults to "/api/auth/login".

    Attributes:
    - auth_scheme (OAuth2PasswordBearer): The OAuth2 authentication scheme.
    - auth_response_model: The response model for authentication.
    - token_response_model: The response model for token generation.

    Methods:
    - create_refresh_token(data: dict[str, Any], expires_delta: Optional[float] = None) -> tuple[str, datetime]:
        Creates a new refresh token.

    - decode_refresh_token(refresh_token: str) -> str:
        Decodes the refresh token and retrieves the email associated with it.

    - create_email_token(data: dict, expires_delta: Optional[float] = None) -> str | None:
        Creates an email token.

    - get_email_from_token(token: str) -> str | None:
        Retrieves the email from the provided token.

    - refresh_access_token(refresh_token: str) -> dict[str, Any] | None:
        Refreshes the access token using the provided refresh token.

    """

    auth_scheme = None  # OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    auth_response_model = None  # OAuth2PasswordRequestForm
    token_response_model = None  # AccessTokenRefreshResponse

    # constructor
    def __init__(
        self,
        secret_key: str,
        algorithm: str | None = None,
        token_url: str = "/api/auth/login",
    ) -> None:
        assert secret_key, "MISSED SECRET_KEY"
        self.auth_scheme = OAuth2PasswordBearer(tokenUrl=token_url)
        self.auth_response_model = OAuth2PasswordRequestForm
        self.token_response_model = AccessTokenRefreshResponse
        super().__init__(secret_key=secret_key, algorithm=algorithm)

    # define a function to generate a new refresh token
    def create_refresh_token(
        self, data: dict[str, Any], expires_delta: Optional[float] = None
    ) -> tuple[str, datetime]:
        """
        Creates a new refresh token.

        Parameters:
        - data (dict[str, Any]): The data to be encoded into the token.
        - expires_delta (Optional[float], optional): The expiration time for the token. Defaults to None.

        Returns:
        - tuple[str, datetime]: The encoded refresh token and its expiration time.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        expire = expire.replace(tzinfo=timezone.utc)
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token, expire

    def decode_refresh_token(self, refresh_token: str) -> str | None:
        """
        Decodes the refresh token and retrieves the email associated with it.

        Parameters:
        - refresh_token (str): The refresh token to decode.

        Returns:
        - str: The email associated with the refresh token.
        - None: If the token is invalid or cannot be decoded.
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    def create_email_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str | None:
        """
        Creates an email token.

        Parameters:
        - data (dict): The data to be encoded into the token.
        - expires_delta (Optional[float], optional): The expiration time for the token. Defaults to None.

        Returns:
        - str | None: The encoded email token.
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        expire = expire.replace(tzinfo=timezone.utc)
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "email_token"}
        )
        encoded_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_token

    def get_email_from_token(self, token: str) -> str | None:
        """
        Retrieves the email from the provided token.

        Parameters:
        - token (str): The token from which to retrieve the email.

        Returns:
        - str | None: The email retrieved from the token.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload and payload["scope"] == "email_token":
                email = payload.get("sub")
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any] | None:
        """
        Refreshes the access token using the provided refresh token.

        Parameters:
        - refresh_token (str): The refresh token to use for refreshing the access token.

        Returns:
        - dict[str, Any] | None: The new access token along with its expiration time.
        """
        if refresh_token:
            email = self.decode_refresh_token(refresh_token)
            if email:
                access_token, expire_token = self.create_access_token(
                    data={"sub": email}
                )
                return {
                    "access_token": access_token,
                    "expire_token": expire_token,
                    "email": email,
                }
        return None


auth_service = Auth(
    secret_key=settings.token_secret_key,
    algorithm=settings.token_algorithm,
    token_url="/api/auth/login",
)
