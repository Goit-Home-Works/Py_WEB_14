"""
This module defines classes for password encryption and JWT token authentication.

Classes:
- PassCrypt: Handles password encryption and verification.
- AuthToken: Handles JWT token encoding, decoding, and access token creation.

"""

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
    """
    Handles password encryption and verification.

    Attributes:
    - pwd_context (CryptContext): The context for password hashing.

    Methods:
    - verify_password(plain_password, hashed_password): Verifies if the plain password matches the hashed password.
    - get_password_hash(password): Returns the hashed version of the password.

    """
    pwd_context: CryptContext

    def __init__(self, scheme: str = "bcrypt") -> None:
        """
        Initializes the PassCrypt class with the specified password hashing scheme.

        Parameters:
        - scheme (str): The password hashing scheme.

        """
        self.pwd_context = CryptContext(schemes=[scheme], deprecated="auto")
        # print("init PassCrypt ", scheme, self.pwd_context)

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies if the plain password matches the hashed password.

        Parameters:
        - plain_password (str): The plain password to verify.
        - hashed_password (str): The hashed password to compare against.

        Returns:
        - bool: True if the passwords match, False otherwise.

        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Returns the hashed version of the password.

        Parameters:
        - password (str): The password to hash.

        Returns:
        - str: The hashed password.

        """
        
        return self.pwd_context.hash(password)


class AuthToken(PassCrypt):
    """
    Handles JWT token encoding, decoding, and access token creation.

    Attributes:
    - SECRET_KEY (str): The secret key for JWT token encryption.
    - ALGORITHM (str): The encryption algorithm for JWT tokens.

    Methods:
    - encode_jwt(to_encode): Encodes data into a JWT token.
    - decode_jwt(token): Decodes a JWT token and retrieves the payload.
    - create_access_token(data, expires_delta): Creates a new access token with optional expiration time.
    - decode_access_token(access_token): Decodes an access token and retrieves the payload.

    """

    SECRET_KEY: str
    ALGORITHM: str

    # constructor
    def __init__(
        self, secret_key: str | None = None, algorithm: str | None = None
    ) -> None:
        """
        Initializes the AuthToken class with the provided secret key and algorithm.

        Parameters:
        - secret_key (str): The secret key for JWT token encryption.
        - algorithm (str): The encryption algorithm for JWT tokens.

        """
        assert secret_key, "MISSED SECRET_KEY"
        self.SECRET_KEY: str = str(secret_key)
        self.ALGORITHM: str = str(algorithm or "HS256")
        assert self.ALGORITHM, "MISSED ALGORITHM"
        super().__init__()

    # JWT operation
    def encode_jwt(self, to_encode) -> str:
        """
        Encodes data into a JWT token.

        Parameters:
        - to_encode (dict): The data to encode into the JWT token.

        Returns:
        - str: The encoded JWT token.

        """
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def decode_jwt(self, token) -> str | None:
        """
        Decodes a JWT token and retrieves the payload.

        Parameters:
        - token (str): The JWT token to decode.

        Returns:
        - str | None: The decoded payload if successful, None otherwise.

        """
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
        """
        Creates a new access token with optional expiration time.

        Parameters:
        - data (dict): The data to encode into the access token.
        - expires_delta (float | None): The optional expiration time for the access token.

        Returns:
        - tuple[str, datetime]: The encoded access token and its expiration datetime.

        """
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
        """
        Decodes an access token and retrieves the payload.

        Parameters:
        - access_token (str): The access token to decode.

        Returns:
        - str | None: The decoded payload if successful, None otherwise.

        """
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
