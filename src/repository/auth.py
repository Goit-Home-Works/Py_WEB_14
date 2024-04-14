import logging
from sqlalchemy.orm import Session


from src.config.config import settings
from src.db.models import User
from src.services.auth import auth_service
from src.repository import users as repository_users


logger = logging.getLogger(f"{settings.app_name}.{__name__}")


async def a_get_current_user(token: str | None, db: Session, cache = None) -> User | None:
    if not token:
        return None
    email = auth_service.decode_jwt(token)
    if email is None:
        return None
    user = await repository_users.get_cache_user_by_email(email, cache)
    if user is None:
        user = await repository_users.get_user_by_email(email, db)
        if user:
            await repository_users.update_cache_user(user, cache)

    return user


async def signup(body, db: Session, cache = None):
    try:
        user = await repository_users.get_user_by_name(body.username, db)
        if user is not None:
            return None
        body.password = auth_service.get_password_hash(body.password)
        # if not body.email:
        #     body.email = body.username
        new_user = await repository_users.create_user(body, db, cache)
    except Exception:
        return None
    return new_user


def login(user: User, password: str, db: Session):
    if user is None:
        return None
    if not auth_service.verify_password(password, user.password):
        return None
    # Generate JWT
    expires_delta = 12*60*60 if settings.app_mode == 'dev' else None
    access_token, expire_token = auth_service.create_access_token(data={"sub": user.email}, expires_delta=expires_delta)
    token = {"access_token": access_token, "token_type": "bearer", "expire_access_token": expire_token}
    refresh_token, expire_token = auth_service.create_refresh_token(data={"sub": user.email})
    token.update({"refresh_token": refresh_token, "expire_refresh_token": expire_token})
    return token


async def update_refresh_token(username: str, refresh_token: str, db: Session):
    return await repository_users.update_by_name_refresh_token(username, refresh_token, db)
