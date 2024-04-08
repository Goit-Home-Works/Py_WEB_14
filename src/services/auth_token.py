from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

from typing import Optional, Any

from passlib.context import CryptContext

from jose import JWTError, jwt

import hashlib
import secrets

load_dotenv()
class PassCrypt:
    pwd_context: CryptContext

    def __init__(self, scheme: str = "bcrypt") -> None:
        self.pwd_context = CryptContext(schemes=[scheme], deprecated="auto")
        # print("init PassCrypt ", scheme, self.pwd_context)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)



class AuthToken(PassCrypt):
    SECRET_KEY: str
    ALGORITHM: str

    # constructor
    def __init__(
        self, secret_key: str | None = None, algorithm: str | None = None
    ) -> None:
        assert secret_key, "MISSED SECRET_KEY"
        self.SECRET_KEY: str = str(secret_key)
        self.ALGORITHM: str = str(algorithm or "HS256")
        assert self.ALGORITHM, "MISSED ALGORITHM"
        super().__init__()

    # JWT operation
    def encode_jwt(self, to_encode) -> str:
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def decode_jwt(self, token) -> str | None:
        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                return email
        except JWTError as e:
            return None

    # define a function to generate a new access token
    def create_access_token(
        self, data: dict[str, Any], expires_delta: Optional[float] = None
    ) -> tuple[str, datetime]:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        expire = expire.replace(tzinfo=timezone.utc)
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = self.encode_jwt(to_encode)
        return encoded_access_token, expire

    def decode_access_token(self, access_token: str) -> str | None:
        try:
            payload = jwt.decode(
                access_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "access_token":
                email = payload["sub"]
                return email
            return None
        except JWTError:
            return None
