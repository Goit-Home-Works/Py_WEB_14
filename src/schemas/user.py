from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


from db.models import Role


class UserModel(BaseModel):
    username: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)


class NewUserResponse(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: str | None
    role: Role

    class Config:
        from_attributes = True



class UserDetailResponse(BaseModel):
    detail: str
    user: UserResponse
