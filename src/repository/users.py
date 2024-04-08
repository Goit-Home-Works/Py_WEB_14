"""
Module Description:
This module contains asynchronous functions for user management, including user creation, retrieval, update, and cache operations.

Functions:
- create_user: Asynchronously creates a new user in the database and updates the cache.
- get_user_by_email: Asynchronously retrieves a user by email from the database.
- get_cache_user_by_email: Asynchronously retrieves a user by email from the cache.
- get_user_by_name: Asynchronously retrieves a user by username from the database.
- update_user_refresh_token: Asynchronously updates a user's refresh token in the database and cache.
- update_by_name_refresh_token: Asynchronously updates a user's refresh token by username in the database and cache.
- update_cache_user: Asynchronously updates user information in the cache.
- confirmed_email: Asynchronously confirms a user's email and updates the cache.
- update_avatar: Asynchronously updates a user's avatar URL in the database and cache.

Dependencies:
- libgravatar: Used for generating user avatars based on email addresses.
- sqlalchemy.orm.Session: SQLAlchemy database session for database operations.
- logging: Standard Python logging module for logging messages.
- pickle: Standard Python module for serializing and deserializing objects.
- redis.asyncio: Asynchronous Redis client for caching user information.
- schemas.user.UserModel: User model schema for creating and updating user information.
- db.models.User: User model class representing the database table for users.
- config.config.settings: Configuration settings for the application.
"""
from libgravatar import Gravatar
from sqlalchemy.orm import Session
import logging
import pickle
import redis.asyncio as redis

from schemas.user import UserModel
from db.models import User
from config.config import settings

logger = logging.getLogger(f"{settings.app_name}.{__name__}")

redis_conn = redis.Redis(host=settings.redis_host, port=int(settings.redis_port), db=0)

async def create_user(body: UserModel, db: Session) -> User | None:
    """
    Asynchronously creates a new user.

    Args:
    - body (UserModel): The user model containing user information.
    - db (Session): The SQLAlchemy database session.

    Returns:
    - User | None: The created user or None if creation fails.
    """

    try:
        g = Gravatar(body.email)
        new_user = User(**body.model_dump(), avatar=g.get_image())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        await update_cache_user(new_user)
    except Exception:
        return None
    return new_user

async def get_user_by_email(email: str | None, db: Session) -> User | None:
    """
    Asynchronously retrieves a user by email.

    Args:
    - email (str | None): The email of the user.
    - db (Session): The SQLAlchemy database session.

    Returns:
    - User | None: The retrieved user or None if not found.
    """

    print(f"{email=} {type(email)=}")
    if email:
        try:
            user = db.query(User).filter_by(email=email).first()
            print(f"get_user_by_email {user=}")
            return user
        except Exception:
            ...
    return None

async def get_cache_user_by_email(email: str) -> User | None:
    """
    Asynchronously retrieves a user from cache by email.

    Args:
    - email (str): The email of the user.

    Returns:
    - User | None: The retrieved user from cache or None if not found.
    """

    if email:
        try:
            user_bytes = await redis_conn.get(f"user:{email}")
            if user_bytes is None:
                return None
            user = pickle.loads(user_bytes)  # type: ignore
            logger.info(f"Get from Redis  {str(user.email)}")
        except Exception as err:
            logger.error(f"Error Redis read {err}")
            user = None
        return user

async def get_user_by_name(username: str | None, db: Session) -> User | None:
    """
    Asynchronously retrieves a user by username.

    Args:
    - username (str | None): The username of the user.
    - db (Session): The SQLAlchemy database session.

    Returns:
    - User | None: The retrieved user or None if not found.
    """

    if username:
        try:
            return db.query(User).filter_by(email=username).first()
        except Exception:
            ...
    return None

async def update_user_refresh_token(
    user: User, refresh_token: str | None, db: Session
) -> str | None:
    """
    Asynchronously updates a user's refresh token.

    Args:
    - user (User): The user to update.
    - refresh_token (str | None): The new refresh token.
    - db (Session): The SQLAlchemy database session.

    Returns:
    - str | None: The updated refresh token or None if update fails.
    """

    if user:
        try:
            user.refresh_token = refresh_token
            db.commit()
            await update_cache_user(user)
            return refresh_token
        except Exception:
            ...
    return None

async def update_by_name_refresh_token(
    username: str | None, refresh_token: str | None, db: Session
) -> str | None:
    """
    Asynchronously updates a user's refresh token by username.

    Args:
    - username (str | None): The username of the user.
    - refresh_token (str | None): The new refresh token.
    - db (Session): The SQLAlchemy database session.

    Returns:
    - str | None: The updated refresh token or None if update fails.
    """

    if username and refresh_token:
        try:
            user = await get_user_by_name(username, db)
            return await update_user_refresh_token(user, refresh_token, db)
        except Exception:
            ...
    return None

async def update_cache_user(user: User):
    """
    Asynchronously updates user information in cache.

    Args:
    - user (User): The user to update.
    """

    if user:
        email = user.email
        try:
            await redis_conn.set(f"user:{email}", pickle.dumps(user))
            await redis_conn.expire(f"user:{email}", 900)
            logger.info(f"Save to Redis {str(user.email)}")
        except Exception as err:
            logger.error(f"Error redis save, {err}")

async def confirmed_email(email: str | None, db: Session) -> bool | None:
    """
    Asynchronously confirms a user's email.

    Args:
    - email (str | None): The email of the user.
    - db (Session): The SQLAlchemy database session.

    Returns:
    - bool | None: True if email is confirmed, False if not confirmed, or None if update fails.
    """

    if email:
        try:
            user = await get_user_by_email(email, db)
            if user:
                user.confirmed = True
                db.commit()
                await update_cache_user(user)
                return True
        except Exception:
            ...
    return None


async def update_avatar(email: str | None, url: str | None, db: Session) -> User:
    """
    Asynchronously updates a user's avatar URL.

    Args:
    - email (str | None): The email of the user.
    - url (str | None): The new avatar URL.
    - db (Session): The SQLAlchemy database session.

    Returns:
    - User: The updated user object.
    """

    user: User = await get_user_by_email(email, db)
    if user:
        user.avatar = url
        db.commit()
        await update_cache_user(user)
    return user
