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
    query = db.query(Contact).filter_by(user_id=user_id)
    if favorite is not None:
        query = query.filter_by(user_id=user_id)
    contacts = query.offset(skip).limit(limit).all()
    return contacts


async def get_contact_by_id(contact_id: int, user_id: int, db: Session):
    contact = db.query(Contact).filter_by(id=contact_id, user_id=user_id).first()
    return contact


async def get_contact_by_email(email: str, user_id: int, db: Session):
    contact = db.query(Contact).filter_by(email=email, user_id=user_id).first()
    return contact


async def create(body: ContactModel, user_id: int, db: Session):
    contact = Contact(**body.model_dump())
    contact.user_id = user_id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(contact_id: int, body: ContactModel, user_id: int, db: Session):
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
    contact = await get_contact_by_id(contact_id, user_id, db)
    if contact:
        contact.favorite = body.favorite
        db.commit()
    return contact


async def delete(contact_id: int, user_id: int, db: Session):
    contact = await get_contact_by_id(contact_id, user_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(param: dict, user_id: int, db: Session):
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
