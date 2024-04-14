import logging
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session


from src.db.database import get_db, get_redis
from src.db.models import User
from src.repository import users as repository_users
from src.routes.auth import get_current_user
from src.config.config import settings
from src.schemas.user import UserResponse
from src.services.cloudinary import Cloudinary

router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


@router.get("/me/", response_model=UserResponse, response_model_exclude_none=True)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Route  Users  read_users_me

    :param current_user: _description_, defaults to Depends(get_current_user)
    :type current_user: User, optional
    :return: _description_
    :rtype: _type_
    """
    return current_user


@router.patch("/avatar", response_model=UserResponse, response_model_exclude_unset=True)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    cache=Depends(get_redis),
):
    """Route  Users  update_avatar_user

    :param file: _description_, defaults to File()
    :type file: UploadFile, optional
    :param current_user: _description_, defaults to Depends(get_current_user)
    :type current_user: User, optional
    :param db: _description_, defaults to Depends(get_db)
    :type db: Session, optional
    :param cache: _description_, defaults to Depends(get_redis)
    :type cache: _type_, optional
    :return: _description_
    :rtype: _type_
    """
    public_id = Cloudinary.generate_public_id_by_email(str(current_user.email))
    r = Cloudinary.upload(file.file, public_id)
    src_url = Cloudinary.generate_url(r, public_id)
    user = await repository_users.update_avatar(current_user.email, src_url, db, cache)  # type: ignore
    return user
