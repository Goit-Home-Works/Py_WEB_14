from datetime import date, timedelta
import logging
from typing import List
from sqlalchemy import select, text, extract, desc

from sqlalchemy.orm import Session


from config.config import settings
from schemas.contact import ContactFavoriteModel, ContactModel
from db.models import Contact

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


async def get_contacts(
    db: Session, user_id: int, skip: int, limit: int, favorite: bool | None = None
) -> List[Contact]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param db: The database session.
    :type db: Session
    :param user_id: The user_id to retrieve contacts for.
    :type user_id: int
    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param favorite: The favorite flag of contact, defaults to None.
    :type favorite: bool | None, optional
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    query = db.query(Contact).filter_by(user_id=user_id)
    if favorite is not None:
        query = query.filter_by(favorite=favorite)
    contacts = query.offset(skip).limit(limit).all()
    # contacts = db.query(Contact).filter_by(user_id = user_id).offset(skip).limit(limit).all()
    return contacts


async def get_contact_by_id(contact_id: int, user_id: int, db: Session) -> Contact:
    """Retrieves a single contact with the specified ID for a specific ID of user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user_id: The user ID to retrieve the contact for.
    :type user_id: int
    :param db: The database session.
    :type db: Session
    :return: Specified contact for specific user.
    :rtype: Contact
    """
    contact = db.query(Contact).filter_by(id=contact_id, user_id=user_id).first()
    return contact


async def get_contact_by_email(email: str, user_id: int, db: Session) -> Contact:
    """Retrieves a single contact with the specified email for a specific ID of user.

    :param email: The email of the contact to retrieve.
    :type email: str
    :param user_id: The user ID to retrieve the contact for.
    :type user_id: int
    :param db: The database session.
    :type db: Session
    :return: Specified contact for specific user.
    :rtype: Contact
    """
    contact = db.query(Contact).filter_by(email=email, user_id=user_id).first()
    return contact


async def create(body: ContactModel, user_id: int, db: Session) -> Contact:
    """Creates a new concact for a specific user.

    :param body: The data for the concact to create.
    :type body: ContactModel
    :param user_id: The user ID to create the note for.
    :type user_id: int
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(**body.model_dump())
    contact.user_id = user_id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(contact_id: int, body: ContactModel, user_id: int, db: Session) -> Contact | None:
    """Updates a single contact with the specified ID for a specific user ID.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactModel
    :param user_id: The user ID to update the contact for.
    :type user_id: int
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None
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


async def favorite_update(contact_id: int, body: ContactFavoriteModel, user_id: int, db: Session) -> Contact | None:
    """Updates favorute status (i.e. "true" or "false") of contact with the specified ID for a specific user ID.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated data with favorite status for the contact.
    :type body: ContactFavoriteModel
    :param user_id: The user ID to update the contact for.
    :type user_id: int
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = await get_contact_by_id(contact_id, user_id, db)
    if contact:
        contact.favorite = body.favorite
        db.commit()
    return contact


async def delete(contact_id: int, user_id: int, db: Session) -> Contact | None:
    """Removes a single contact with the specified ID for a specific user ID.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param user_id: The user ID to remove the contact for.
    :type user_id: int
    :param db: The database session.
    :type db: Session
    :return: The removed contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = await get_contact_by_id(contact_id, user_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(param: dict, user_id: int, db: Session) -> List[Contact]:
    """Retrieves a list of contacts for a specific user with specified search and pagination parameters.

    :param param: This is dictionary of parameters for search contacts. Dictionary keys:

        - first_name - (optional) First name of contact
        - last_name - (optional) Last name of contact
        - email - (optional) email of contact
        - skip - The number of contacts to skip
        - limit - The maximum number of contacts to return

    :type param: dict{"first_name": str, "last_name": str, "email": str, "skip": int, "limit": int}
    :param user_id: The user ID to search the contact for.
    :type user_id: int
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
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
    """Function for replacing the year in the date, if the date is not in the year to be replaced,
    then we get the next day for this date in this year.

    :param d: Source date
    :type d: date
    :param year: Year to replace in date
    :type year: int
    :return: Date with the year replaced
    :rtype: date
    """
    try:
        d = d.replace(year=year)  # 29.02.1988
    except ValueError as err:
        logger.debug(f"date_replace_year b:  {d}")
        d = d + timedelta(days=1)  # 29.02.1988 -> 01.03.1988
        d = d.replace(year=year)  # 01.03.1988 -> 01.03.2023
        logger.debug(f"date_replace_year a:  {d}")
    return d


# SELECT * FROM public.contacts where user_id = 6 and EXTRACT(MONTH FROM contacts.birthday) IN (1,2,3);


async def search_birthday(param: dict, user_id: int, db: Session) -> List[Contact]:
    """
    Retrieves a list of contacts for a specific user with the specified birthday search parameters
    for the next few days and pagination parameters.

    :param param: This is dictionary of parameters for search contacts. Dictionary keys:

        - days - Search for contacts whose birthdays are within the next number of days from the current date, defaults to 7
        - skip - The number of contacts to skip
        - limit - The maximum number of contacts to return

    :type param: dict{'days': int, 'skip': int, 'limit': int}
    :param user_id: The user ID to search the contact for.
    :type user_id: int
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    days: int = int(param.get("days", 7)) + 1
    # days = 67
    date_now = param.get("fixed_now",  date.today())
    # date_now = date.today()
    # date_now = date(2023, 2, 25)
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
        select(Contact)
        .where(Contact.user_id == user_id, extract("MONTH", Contact.birthday).in_(list_month))  # type: ignore
        .order_by(desc(Contact.birthday))  # type: ignore
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