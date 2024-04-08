from sqlalchemy import Boolean, Column, Enum, Date, DateTime, Integer, String, Text, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

from datetime import date
import enum

Base = declarative_base()


class Contact(Base):
        
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
    admin: str = "admin"  # type: ignore
    moderator: str = "moderator"  # type: ignore
    user: str = "user"  # type: ignore


class User(Base):
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
