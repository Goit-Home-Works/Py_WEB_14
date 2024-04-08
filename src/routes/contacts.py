from typing import List

from fastapi import Path, Depends, HTTPException, Query, status, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from db.database import get_db
from schemas.contact import ContactFavoriteModel, ContactModel, ContactResponse
from repository import contacts as repository_contacts
from db.models import User
from routes import auth
from config.config import settings

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/search", response_model=List[ContactResponse])
async def search_contacts(
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    skip: int = 0,
    limit: int = Query(default=10, le=100, ge=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    contacts = None
    if first_name or last_name or email:
        param = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "skip": skip,
            "limit": limit,
        }
        user_id: int = current_user.id  # type: ignore
        contacts = await repository_contacts.search_contacts(param, user_id, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contacts


@router.get("/search/birtdays", response_model=List[ContactResponse])
async def search_contacts_birthday(
    days: int = Query(default=7, le=30, ge=1),
    skip: int = 0,
    limit: int = Query(default=10, le=100, ge=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    contacts = None
    if days:
        param = {
            "days": days,
            "skip": skip,
            "limit": limit,
        }
        contacts = await repository_contacts.search_birthday(param, current_user.id, db)  # type: ignore
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contacts


@router.get("", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = 0,
    limit: int = Query(default=10, le=100, ge=10),
    favorite: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    contacts = await repository_contacts.get_contacts(
        db=db, user_id=current_user.id, skip=skip, limit=limit, favorite=favorite  # type: ignore
    )
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user.id, db)  # type: ignore
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    description=f"No more than  {settings.create_limiter_times} requests per {settings.create_limiter_seconds} seconds",
    dependencies=[
        Depends(
            RateLimiter(
                times=settings.create_limiter_times,
                seconds=settings.create_limiter_seconds,
            )
        )
    ],
)
async def create_contact(
    body: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    contact = await repository_contacts.get_contact_by_email(body.email, current_user.id, db)
    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Email is exist!"
        )
    try:
        contact = await repository_contacts.create(body, current_user.id, db)
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Error: {err}"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    contact = await repository_contacts.update(contact_id, body, current_user.id, db)  # type: ignore
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.patch("/{contact_id}/favorite", response_model=ContactResponse)
async def favorite_update(
    body: ContactFavoriteModel,
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    contact = await repository_contacts.favorite_update(contact_id, body, current_user.id, db)  # type: ignore
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Only admin",
)
async def remove_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
):
    contact = await repository_contacts.delete(contact_id, current_user.id, db)  # type: ignore
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return None
