"""
This module defines Pydantic models for handling contacts.

Models:
- ContactModel: Represents the structure of a contact including first name, last name, email, phone, birthday, comments, and favorite status.
- ContactFavoriteModel: Represents the structure of a favorite flag for a contact.
- ContactResponse: Represents the response structure for a contact including its details and associated user information.

"""

from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr
from schemas.user import UserResponse

class ContactModel(BaseModel):
    """
    Represents the structure of a contact.

    Attributes:
    - first_name (str): The first name of the contact.
    - last_name (str): The last name of the contact.
    - email (EmailStr): The email address of the contact.
    - phone (str): The phone number of the contact (optional).
    - birthday (date): The birthday of the contact (optional).
    - comments (str): Additional comments about the contact (optional).
    - favorite (bool): Indicates whether the contact is marked as a favorite.

    """
    first_name: str = Field(
        default="",
        examples=["Taras", "Ostap"],
        min_length=1,
        max_length=25,
        title="Ім'я",
    )
    last_name: str = Field(
        default="",
        examples=["Shevcheko", "Bulba"],
        min_length=1,
        max_length=25,
        title="Прізвище",
    )
    email: EmailStr
    phone: str | None = Field(
        None,
        examples=["+380 44 123-4567", "+380 (44) 1234567", "+380441234567"],
        max_length=25,
        title="Номер телефону",
    )
    birthday: date | None = None
    comments: str | None = Field(default=None, title="Додаткові дані")
    favorite: bool = False


class ContactFavoriteModel(BaseModel):
    """
    Represents the structure of a favorite flag for a contact.

    Attributes:
    - favorite (bool): Indicates whether the contact is marked as a favorite.

    """

    favorite: bool = False

    # pattern=r"^+[0-9\s\(\)-]+$


class ContactResponse(BaseModel):
    """
    Represents the response structure for a contact.

    Attributes:
    - id (int): The ID of the contact.
    - first_name (str): The first name of the contact.
    - last_name (str): The last name of the contact.
    - email (EmailStr): The email address of the contact.
    - phone (str): The phone number of the contact.
    - birthday (date): The birthday of the contact.
    - comments (str): Additional comments about the contact.
    - favorite (bool): Indicates whether the contact is marked as a favorite.
    - created_at (datetime): The date and time when the contact was created.
    - updated_at (datetime): The date and time when the contact was last updated.
    - user (UserResponse): Information about the user associated with the contact.

    """
    id: int
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    phone: str | None
    birthday: date | None
    comments: str | None
    favorite: bool
    created_at: datetime
    updated_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True
