import logging
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session


from db.database import get_db
from db.models import User
from repository import users as repository_users
from routes.auth import get_current_user
from config.config import settings
from schemas.user import UserResponse
from services.cloudinary import Cloudinary

router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


@router.get("/me/", response_model=UserResponse, response_model_exclude_none=True)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/avatar", response_model=UserResponse, response_model_exclude_unset=True)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    public_id = Cloudinary.generate_public_id_by_email(str(current_user.email))
    r = Cloudinary.upload(file.file, public_id)
    src_url = Cloudinary.generate_url(r, public_id)
    print(f"{public_id=}")
    print(f"{src_url=}")
    user = await repository_users.update_avatar(current_user.email, src_url, db)  # type: ignore
    return user

