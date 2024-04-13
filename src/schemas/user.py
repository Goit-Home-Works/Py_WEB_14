"""
This module defines Pydantic models related to user data.

Models:
- UserModel: Represents the structure of user data including username, email, and password.
- NewUserResponse: Represents the response structure for a new user.
- UserResponse: Represents the response structure for a user including user ID, username, email, avatar, and role.
- UserDetailResponse: Represents the response structure for user details including a detail message and user data.

"""

from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, ConfigDict


from db.models import Role


class UserModel(BaseModel):
    """
    Represents the structure of user data.

    Attributes:
    - username (str): The username of the user (2-150 characters).
    - email (EmailStr): The email address of the user.
    - password (str): The password of the user (6-64 characters).

    """
    username: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)


class NewUserResponse(BaseModel):
    """
    Represents the response structure for a new user.

    Attributes:
    - username (str): The username of the new user.

    """

    username: str


class UserResponse(BaseModel):
    """
    Represents the response structure for a user.

    Attributes:
    - id (int): The ID of the user.
    - username (str): The username of the user.
    - email (str): The email address of the user.
    - avatar (str | None): The avatar of the user (or None if not available).
    - role (Role): The role of the user.

    """
    id: int
    username: str
    email: str
    avatar: str | None
    role: Role

    # class Config:
    #     from_attributes = True

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(BaseModel):
    """
    Represents the response structure for user details.

    Attributes:
    - detail (str): A message providing details about the response.
    - user (UserResponse): The user data.

    """
    detail: str
    user: UserResponse
