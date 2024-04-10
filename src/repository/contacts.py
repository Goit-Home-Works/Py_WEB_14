"""
This module contains functions and methods related to managing contacts in the database.

Functions:
- get_contacts: Asynchronously retrieves contacts based on user ID, skip, and limit.
- get_contact_by_id: Asynchronously retrieves a contact by its ID and user ID.
- get_contact_by_email: Asynchronously retrieves a contact by its email and user ID.
- create: Asynchronously creates a new contact in the database.
- update: Asynchronously updates an existing contact in the database.
- favorite_update: Asynchronously updates the favorite status of a contact in the database.
- delete: Asynchronously deletes a contact from the database.
- search_contacts: Asynchronously searches for contacts based on various parameters.
- date_replace_year: Replaces the year of a date with a new year, handling exceptions.
- search_birthday: Asynchronously searches for contacts with upcoming birthdays within a specified range.

Parameters:
- db (Session): The SQLAlchemy database session.
- user_id (int): The ID of the user associated with the contacts.
- body (ContactModel or ContactFavoriteModel): The request body containing contact information.
- contact_id (int): The ID of the contact.
- email (str): The email of the contact.
- param (dict): Dictionary containing search parameters.
- d (date): The date object to be modified.
- year (int): The new year to replace in the date.
- days (int): The number of days within which to search for upcoming birthdays.
- date_now (date): The current date.
- date_now_year (int): The year component of the current date.
- date_now_month (int): The month component of the current date.
- date_last_month (int): The month component of the date after the specified number of days.
- list_month (List[int]): List of months to search for upcoming birthdays.
- contacts (List[Contact]): List of contacts retrieved from the database.
- query (sqlalchemy.sql.selectable.Select): SQL query for retrieving contacts.
- contacts_q (List[Contact]): List of contacts returned by the query.
- birthday (date): The birthday of a contact.
- bd (date): Modified birthday with the current year.
- diff_bd (timedelta): Difference between the modified birthday and the current date.
- skip (int): Number of contacts to skip in the results.
- limit (int): Maximum number of contacts to return in the results.
"""

from datetime import date, timedelta
import logging
from typing import List

import sqlalchemy
from sqlalchemy.orm import Session

from config.config import settings
from schemas.contact import ContactModel, ContactFavoriteModel
from db.models import Contact


logger = logging.getLogger(f"{settings.app_name}.{__name__}")

async def get_contacts(
    db: Session, user_id: int, skip: int, limit: int, favorite: bool | None = None
):
    """
    Asynchronously retrieves contacts based on user ID, skip, and limit.

    Args:
    - db (Session): The SQLAlchemy database session.
    - user_id (int): The ID of the user.
    - skip (int): Number of contacts to skip.
    - limit (int): Maximum number of contacts to return.
    - favorite (bool | None, optional): Filter contacts by favorite status. Defaults to None.

    Returns:
    - List[Contact]: List of contacts.
    """
    query = db.query(Contact).filter_by(user_id=user_id)
    if favorite is not None:
        query = query.filter_by(user_id=user_id)
    contacts = query.offset(skip).limit(limit).all()
    return contacts


async def get_contact_by_id(contact_id: int, user_id: int, db: Session):
    """
    Asynchronously retrieves a contact by its ID and user ID.

    Args:
    - contact_id (int): The ID of the contact.
    - user_id (int): The ID of the user.
    - db (Session): The SQLAlchemy database session.

    Returns:
    - Contact | None: The retrieved contact, or None if not found.
    """
    contact = db.query(Contact).filter_by(id=contact_id, user_id=user_id).first()
    return contact


async def get_contact_by_email(email: str, user_id: int, db: Session):
    """
    Retrieve a contact by email and user_id.

    Parameters:
    email (str): The email of the contact.
    user_id (int): The id of the user.
    db (Session): The database session.

    Returns:
    Contact: The contact object.
    """
    contact = db.query(Contact).filter_by(email=email, user_id=user_id).first()
    return contact


async def create(body: ContactModel, user_id: int, db: Session):
    """
    Create a new contact.

    Parameters:
    body (ContactModel): The contact data.
    user_id (int): The id of the user.
    db (Session): The database session.

    Returns:
    Contact: The created contact object.
    """
    contact = Contact(**body.model_dump())
    contact.user_id = user_id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(contact_id: int, body: ContactModel, user_id: int, db: Session):
    """
    Update an existing contact.

    Parameters:
    contact_id (int): The id of the contact.
    body (ContactModel): The updated contact data.
    user_id (int): The id of the user.
    db (Session): The database session.

    Returns:
    Contact: The updated contact object.
    """
    contact = await get_contact_by_id(contact_id, user_id, db)
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.comments = body.comments
        contact.favorite = body.favorite
        db.commit()
    return contact


async def favorite_update(
    contact_id: int, body: ContactFavoriteModel, user_id: int, db: Session
):
    """
    Update the favorite status of a contact.

    Parameters:
    contact_id (int): The id of the contact.
    body (ContactFavoriteModel): The updated favorite status.
    user_id (int): The id of the user.
    db (Session): The database session.

    Returns:
    Contact: The updated contact object.
    """
    contact = await get_contact_by_id(contact_id, user_id, db)
    if contact:
        contact.favorite = body.favorite
        db.commit()
    return contact


async def delete(contact_id: int, user_id: int, db: Session):
    """
    Delete a contact.

    Parameters:
    contact_id (int): The id of the contact.
    user_id (int): The id of the user.
    db (Session): The database session.

    Returns:
    Contact: The deleted contact object.
    """
    contact = await get_contact_by_id(contact_id, user_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(param: dict, user_id: int, db: Session):
    """
    Search for contacts based on parameters.

    Parameters:
    param (dict): The search parameters.
    user_id (int): The id of the user.
    db (Session): The database session.

    Returns:
    List[Contact]: A list of contact objects that match the search criteria.
    """
    query = db.query(Contact).filter_by(user_id=user_id)
    first_name = param.get("first_name")
    last_name = param.get("last_name")
    email = param.get("email")
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    contacts = query.offset(param.get("skip")).limit(param.get("limit"))
    return contacts


def date_replace_year(d: date, year: int) -> date:
    """
    Replace the year of a date, handling the case where the day does not exist in the new year.

    Parameters:
    d (date): The date to modify.
    year (int): The new year.

    Returns:
    date: The modified date.
    """
    try:
        d = d.replace(year=year)
    except ValueError as err:
        logger.debug(f"date_replace_year b:  {d}")
        d = d + timedelta(days=1)
        d = d.replace(year=year)
        logger.debug(f"date_replace_year a:  {d}")
    return d


# SELECT * FROM public.contacts where user_id = 6 and EXTRACT(MONTH FROM contacts.birthday) IN (1,2,3);


async def search_birthday(param: dict, user_id: int, db: Session) -> List[Contact]:
    """
    Search for contacts whose birthday is within a certain number of days.

    Parameters:
    param (dict): The search parameters.
    user_id (int): The id of the user.
    db (Session): The database session.

    Returns:
    List[Contact]: A list of contact objects whose birthday is within the specified number of days.
    """
    days: int = int(param.get("days", 7)) + 1
    date_now = date.today()
    date_now_year = date_now.year
    date_now_month = date_now.month
    date_last_month = (date_now + timedelta(days=days + 1)).month
    # logger.debug(f"{date_now_month=}, ${date_last_month=} {date_now + timedelta(days=days+1)}")
    list_month = [date_now_month]
    while date_last_month != date_now_month:
        # logger.debug(f"{date_last_month=}, {date_now_month=}")
        list_month.append(date_last_month)
        date_last_month = 12 if date_last_month <= 1 else date_last_month - 1

    contacts = []
    query = (
        sqlalchemy.select(Contact)
        .where(Contact.user_id == user_id, sqlalchemy.extract("MONTH", Contact.birthday).in_(list_month))  # type: ignore
        .order_by(sqlalchemy.desc(Contact.birthday))  # type: ignore
    )
    contacts_q = db.execute(query).scalars()
    for contact in contacts_q:
        birthday: date | None = contact.birthday  # type: ignore
        if birthday is not None:
            bd = date_replace_year(birthday, date_now_year)
            if bd < date_now:
                bd = date_replace_year(birthday, date_now_year + 1)
            diff_bd = bd - date_now
            if diff_bd.days <= days:
                logger.debug(f"f{str(contact)=}")
                contacts.append(contact)
    skip = int(param.get("skip", 0))
    limit = int(param.get("limit", 0))
    return contacts[skip : skip + limit]
