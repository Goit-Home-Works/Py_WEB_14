"""
This module defines SQLAlchemy models for managing contacts and users in a database.

Contact:
- Represents a contact with attributes like first name, last name, email, phone, birthday, comments, etc.
- Attributes:
    - id: Primary key of the contact.
    - first_name: First name of the contact.
    - last_name: Last name of the contact.
    - email: Email address of the contact.
    - phone: Phone number of the contact.
    - birthday: Birthday of the contact.
    - comments: Additional comments about the contact.
    - favorite: Indicates whether the contact is marked as favorite.
    - created_at: Timestamp indicating when the contact was created.
    - updated_at: Timestamp indicating when the contact was last updated.
    - user_id: Foreign key referencing the user who owns the contact.
    - user: Relationship to the User model representing the owner of the contact.

User:
- Represents a user with attributes like username, email, password, role, etc.
- Attributes:
    - id: Primary key of the user.
    - username: Username of the user.
    - email: Email address of the user.
    - password: Password of the user.
    - refresh_token: Refresh token for the user's session (optional).
    - avatar: URL of the user's avatar image (optional).
    - role: Role of the user, which is an Enum with possible values 'admin', 'moderator', or 'user'.
    - confirmed: Indicates whether the user's email address is confirmed.

Role:
- Enum representing user roles with values 'admin', 'moderator', and 'user'.

"""
from sqlalchemy import Boolean, Column, Enum, Date, DateTime, Integer, String, Text, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

from datetime import date
import enum

Base = declarative_base()


class Contact(Base):
    """Represents a contact in the database."""
        
    __tablename__ = "contacts"

    id: int | Column[int] = Column(Integer, primary_key=True, index=True)
    first_name: str | Column[str] | None = Column(String)
    last_name: str | Column[str] | None = Column(String)
    email: str | Column[str] = Column(String)
    phone: str | Column[str] | None = Column(String)
    birthday: date | Column[date] | None = Column(Date)
    comments: str | Column[str] | None = Column(Text)
    favorite: bool | Column[bool] | None = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id: int | Column[int] = Column(
        Integer, ForeignKey("users.id"), nullable=False, default=1
    )
    user = relationship("User", backref="contacts")
    # , cascade="all, delete-orphan"

    def __str__(self):
        return f"id: {self.id}, email: {self.email}, username: {self.first_name} {self.last_name}, birthday: {self.birthday}"


class Role(enum.Enum):
    """Enumeration representing user roles."""
    admin: str = "admin"  # type: ignore
    moderator: str = "moderator"  # type: ignore
    user: str = "user"  # type: ignore


class User(Base):
    """Represents a user in the database."""
    __tablename__ = "users"

    id: int | Column[int] = Column(Integer, primary_key=True)
    username: str | Column[str] = Column(String(150), nullable=False)
    email: str | Column[str] = Column(String(150), nullable=False, unique=True)
    password: str | Column[str] = Column(String(255), nullable=False)
    refresh_token: str | Column[str] | None = Column(String(255), nullable=True)
    avatar: str | Column[str] | None = Column(String(255), nullable=True)
    role: Enum | Column[Enum] = Column("roles", Enum(Role), default=Role.user)
    confirmed: bool | Column[bool] | None = Column(Boolean, default=False, nullable=True)


    def __str__(self):
        return f"id: {self.id}, email: {self.email}, username: {self.username}"
