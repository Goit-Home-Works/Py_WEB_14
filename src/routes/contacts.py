"""
This module defines the API routes related to managing contacts.

It includes endpoints for searching contacts, retrieving contacts, creating new contacts,
updating existing contacts, and deleting contacts. Additionally, it provides rate limiting
functionality for creating new contacts to prevent abuse.

Endpoints:
- /contacts/search: Search for contacts based on various criteria.
- /contacts/search/birthdays: Retrieve contacts with upcoming birthdays.
- /contacts: Retrieve, create, and update contacts.
- /contacts/{contact_id}: Retrieve, update, or delete a specific contact.

All endpoints require authentication and are rate-limited to prevent abuse.
"""

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
) -> List[ContactResponse]:
    """
    Searches for contacts based on the provided criteria.

    Parameters:
    - first_name (str, optional): The first name of the contact.
    - last_name (str, optional): The last name of the contact.
    - email (str, optional): The email address of the contact.
    - skip (int, optional): Number of records to skip.
    - limit (int, optional): Maximum number of records to return.
    - db (Session): The database session.
    - current_user (User): The current authenticated user.

    Returns:
    - List[ContactResponse]: A list of contacts matching the search criteria.

    Raises:
    - HTTPException: If no contacts are found.
    """
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
) -> List[ContactResponse]:
    """
    Searches for contacts with birthdays within a specified number of days.

    Parameters:
    - days (int, optional): Number of days within which to search for birthdays.
    - skip (int, optional): Number of records to skip.
    - limit (int, optional): Maximum number of records to return.
    - db (Session): The database session.
    - current_user (User): The current authenticated user.

    Returns:
    - List[ContactResponse]: A list of contacts with birthdays within the specified days.

    Raises:
    - HTTPException: If no contacts are found.
    """
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
) -> List[ContactResponse]:
    """
    Retrieves contacts for the current user.

    Parameters:
    - skip (int, optional): Number of records to skip.
    - limit (int, optional): Maximum number of records to return.
    - favorite (bool, optional): If True, only favorite contacts will be returned.
    - db (Session): The database session.
    - current_user (User): The current authenticated user.

    Returns:
    - List[ContactResponse]: A list of contacts belonging to the current user.

    Raises:
    - HTTPException: If no contacts are found.
    """
    contacts = await repository_contacts.get_contacts(
        db=db, user_id=current_user.id, skip=skip, limit=limit, favorite=favorite  # type: ignore
    )
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user),
) -> ContactResponse:
    """
    Retrieves a contact by its ID.

    Parameters:
    - contact_id (int): The ID of the contact to retrieve.
    - db (Session): The database session.
    - current_user (User): The current authenticated user.

    Returns:
    - ContactResponse: The contact with the specified ID.

    Raises:
    - HTTPException: If the contact with the specified ID is not found.
    """
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
) -> ContactResponse:
    """
    Creates a new contact for the current user.

    Parameters:
    - body (ContactModel): The data representing the new contact.
    - db (Session): The database session.
    - current_user (User): The current authenticated user.

    Returns:
    - ContactResponse: The newly created contact.

    Raises:
    - HTTPException: If the email of the new contact already exists or if there's an integrity error.
    """
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
) -> ContactResponse:
    """
    Updates an existing contact.

    Parameters:
    - body (ContactModel): The data representing the updated contact.
    - contact_id (int): The ID of the contact to update.
    - db (Session): The database session.
    - current_user (User): The current authenticated user.

    Returns:
    - ContactResponse: The updated contact.

    Raises:
    - HTTPException: If the contact with the specified ID is not found.
    """
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
) -> ContactResponse:
    """
    Updates the favorite status of a contact.

    Parameters:
    - body (ContactFavoriteModel): The data representing the favorite status update.
    - contact_id (int): The ID of the contact to update.
    - db (Session): The database session.
    - current_user (User): The current authenticated user.

    Returns:
    - ContactResponse: The contact with the updated favorite status.

    Raises:
    - HTTPException: If the contact with the specified ID is not found.
    """
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
) -> None:
    """
    Removes a contact.

    Parameters:
    - contact_id (int): The ID of the contact to remove.
    - db (Session): The database session.
    - current_user (User): The current authenticated user.

    Raises:
    - HTTPException: If the contact with the specified ID is not found.
    """
    contact = await repository_contacts.delete(contact_id, current_user.id, db)  # type: ignore
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return None
