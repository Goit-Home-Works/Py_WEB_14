"""
This module defines API routes related to user management.

It includes endpoints for retrieving the current user profile (`/users/me/`) and updating user avatars (`/users/avatar`).

Endpoints:
- /users/me/: Retrieve the profile of the current authenticated user.
- /users/avatar: Update the avatar of the current authenticated user.

All endpoints require authentication.

Dependencies:
- get_current_user: Dependency function to retrieve the current authenticated user.
- get_db: Dependency function to get the database session.

This module also uses the Cloudinary service for avatar management.

"""

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
async def read_users_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    Retrieve the profile of the current authenticated user.

    Parameters:
    - current_user (User): The current authenticated user.

    Returns:
    - UserResponse: The response containing the user profile.

    """
    return current_user


@router.patch("/avatar", response_model=UserResponse, response_model_exclude_unset=True)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Update the avatar of the current authenticated user.

    Parameters:
    - file (UploadFile): The avatar image file to upload.
    - current_user (User): The current authenticated user.
    - db (Session): The database session.

    Returns:
    - UserResponse: The updated user profile with the new avatar URL.

    """
    public_id = Cloudinary.generate_public_id_by_email(str(current_user.email))
    r = Cloudinary.upload(file.file, public_id)
    src_url = Cloudinary.generate_url(r, public_id)
    print(f"{public_id=}")
    print(f"{src_url=}")
    user = await repository_users.update_avatar(current_user.email, src_url, db)  # type: ignore
    return user
