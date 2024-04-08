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
    if username:
        try:
            return db.query(User).filter_by(email=username).first()
        except Exception:
            ...
    return None

async def update_user_refresh_token(
    user: User, refresh_token: str | None, db: Session
) -> str | None:
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
    if username and refresh_token:
        try:
            user = await get_user_by_name(username, db)
            return await update_user_refresh_token(user, refresh_token, db)
        except Exception:
            ...
    return None

async def update_cache_user(user: User):
    if user:
        email = user.email
        try:
            await redis_conn.set(f"user:{email}", pickle.dumps(user))
            await redis_conn.expire(f"user:{email}", 900)
            logger.info(f"Save to Redis {str(user.email)}")
        except Exception as err:
            logger.error(f"Error redis save, {err}")

async def confirmed_email(email: str | None, db: Session) -> bool | None:
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
    user: User = await get_user_by_email(email, db)
    if user:
        user.avatar = url
        db.commit()
        await update_cache_user(user)
    return user
