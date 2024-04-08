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

    def decode_refresh_token(self, refresh_token: str):
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
