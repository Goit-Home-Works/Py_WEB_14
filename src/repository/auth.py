import logging
from typing import Annotated

from fastapi import Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


from config.config import settings
from db.models import User
from services.auth import auth_service
from repository import users as repository_users

from db.database import get_db

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


async def a_get_current_user(token: str | None, db: Session) -> User | None:
    if not token:
        return None
    email = auth_service.decode_jwt(token)
    if email is None:
        return None
    user = await repository_users.get_cache_user_by_email(email)
    if user is None:
        user = await repository_users.get_user_by_email(email, db)
        if user:
            await repository_users.update_cache_user(user)

    return user


async def signup(body, db: Session):
    try:
        user = await repository_users.get_user_by_name(body.username, db)
        print(f"get_user_by_name: ", user)
        if user is not None:
            return None
        body.password = auth_service.get_password_hash(body.password)
        # if not body.email:
        #     body.email = body.username
        new_user = await repository_users.create_user(body, db)
        print(f"HELLO {new_user=}")
    except Exception:
        return None
    return new_user


def login(user: User, password: str, db: Session):
    print(f"{user=}")
    print(f"{user.password=}")
    print(f"{password=}")
    if user is None:
        return None
    verified_password = auth_service.verify_password(password, user.password)
    print(f"{verified_password=}")
    if not verified_password:
        return None
    # # Generate JWT
    token = generate_tokens(user)
    print(f"{token=}")
    return token


def generate_tokens(user: User):
    # Generate JWT
    expires_delta = 12 * 60 * 60 if settings.app_mode == "dev" else None
    access_token, expire_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=expires_delta
    )
    token = {
        "access_token": access_token,
        "token_type": "bearer",
        "expire_access_token": expire_token,
    }
    refresh_token, expire_token = auth_service.create_refresh_token(
        data={"sub": user.email}
    )
    token.update({"refresh_token": refresh_token, "expire_refresh_token": expire_token})
    return token


async def update_refresh_token(username: str, refresh_token: str, db: Session):
    return await repository_users.update_by_name_refresh_token(username, refresh_token, db)
