import logging
import pickle
from libgravatar import Gravatar
from sqlalchemy.orm import Session
import redis.asyncio as redis

from config.config import settings
from schemas.user import UserModel
from db.models import User


logger = logging.getLogger(f"{settings.app_name}.{__name__}")


# redis_conn = redis.Redis(host=settings.redis_host, port=int(settings.redis_port), db=0)
# redis_conn: redis.Redis = get_redis()

async def get_cache_user_by_email(email: str, cache = None ) -> User | None:
    """Get user from cache by email if it is or None if not found

    :param email: User's email
    :type email: str
    :param cache: cache service, defaults to None
    :type cache: cache service connection like redis, optional
    :return: User object or None
    :rtype: User | None
    """
    if email:
        user_bytes = None
        try:
            if cache:
                user_bytes = await cache.get(f"user:{email}")
            if user_bytes is None:
                return None
            user = pickle.loads(user_bytes)  # type: ignore
            logger.info(f"Get from Redis  {str(user.email)}")
        except Exception as err:
            logger.error(f"Error Redis read {err}")
            user = None
        return user


async def update_cache_user(user: User, cache = None):
    """Update user on cache

    :param user: User
    :type user: User
    :param cache: cache service, defaults to None
    :type cache: cache service connection like redis, optional
    """
    if user and cache:
        email = user.email
        try:
            await cache.set(f"user:{email}", pickle.dumps(user))
            await cache.expire(f"user:{email}", 900)
            logger.info(f"Save to Redis {str(user.email)}")
        except Exception as err:
            logger.error(f"Error redis save, {err}")


async def create_user(body: UserModel, db: Session, cache = None) -> User | None:
    """create_user

    :param body: User Model
    :type body: UserModel
    :param db: DB conenction
    :type db: Session
    :param cache: cache service, defaults to None
    :type cache: cache service connection like redis, optional
    :return: User object or None
    :rtype: User | None
    """
    try:
        g = Gravatar(body.email)
        new_user = User(**body.model_dump(), avatar=g.get_image())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        await update_cache_user(new_user, cache)
    except Exception:
        return None
    return new_user


async def get_user_by_email(email: str | None, db: Session) -> User | None:
    """get_user_by_email

    :param email: User's email
    :type email: str | None
    :param db: DB conenction
    :type db: Session
    :return: User object or None
    :rtype: User | None
    """
    if email:
        try:
            return db.query(User).filter_by(email=email).first()
        except Exception:
            ...
    return None


async def get_user_by_name(username: str | None, db: Session) -> User | None:
    """get_user_by_name

    :param email: User's username
    :type email: str | None
    :param db: DB conenction
    :type db: Session
    :return: User object
    :rtype: User | None
    """
    if username:
        try:
            return db.query(User).filter_by(email=username).first()
        except Exception:
            ...
    return None


async def update_user_refresh_token(user: User, refresh_token: str | None, db: Session, cache = None) -> str | None:
    """update_user_refresh_token

    :param user: User
    :type user: User
    :param refresh_token: refresh token
    :type refresh_token: str | None
    :param db: DB conenction
    :type db: Session
    :param cache: cache service, defaults to None
    :type cache: cache service connection like redis, optional
    :return: refresh_token
    :rtype: str | None
    """
    if user:
        try:
            user.refresh_token = refresh_token
            db.commit()
            await update_cache_user(user, cache)
            return refresh_token
        except Exception:
            ...
    return None


async def update_by_name_refresh_token(
    username: str | None, refresh_token: str | None, db: Session
) -> str | None:
    """update_by_name_refresh_token by username

    :param username: username
    :type username: str | None
    :param refresh_token: refresh_token
    :type refresh_token: str | None
    :param db: DB conenction
    :type db: Session
    :return: refresh_token
    :rtype: str | None
    """
    if username and refresh_token:
        try:
            user = await get_user_by_name(username, db)
            return await update_user_refresh_token(user, refresh_token, db)
        except Exception:
            ...
    return None


async def confirmed_email(email: str | None, db: Session, cache = None) -> bool | None:
    """set state of confirmed email

    :param email: User's email
    :type email: str | None
    :param db:  DB conenction
    :type db: Session
    :param cache: cache service, defaults to None
    :type cache: cache service connection like redis, optional
    :return: true if success, None if fail
    :rtype: bool | None
    """
    if email:
        try:
            user = await get_user_by_email(email, db)
            if user:
                user.confirmed = True
                db.commit()
                await update_cache_user(user, cache)
                return True
        except Exception:
            ...
    return None


async def update_avatar(email: str | None, url: str | None, db: Session, cache = None) -> User:
    """_summary_

    :param email: update User's avatar
    :type email: str | None
    :param url: email
    :type url: str | None
    :param db:  DB conenction
    :type db: Session
    :param cache: cache service, defaults to None
    :type cache: cache service connection like redis, optional
    :return: User object
    :rtype: User
    """
    user: User = await get_user_by_email(email, db)
    if user:
        user.avatar = url
        db.commit()
        await update_cache_user(user, cache)
    return user
