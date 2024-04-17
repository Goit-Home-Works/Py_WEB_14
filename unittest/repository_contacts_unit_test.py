from datetime import date, timedelta
import logging
import colorlog
import functools
import sys
import os
import unittest
from unittest.mock import MagicMock
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import select, text, extract, desc

RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

hw_path: str = str(Path(__file__).resolve().parent.parent.joinpath("src"))
sys.path.append(hw_path)
# print(f"{hw_path=}", sys.path)

from db.models import User, Contact
from schemas.contact import ContactModel, ContactFavoriteModel

from repository.contacts import (
    get_contacts,
    get_contact_by_id,
    get_contact_by_email,
    create,
    update,
    delete,
    favorite_update,
    search_birthday,
)
from config.config import settings

# Set up logging configuration
logger = logging.getLogger(f"{settings.app_name}")
logger.setLevel(logging.INFO)

# Set up custom formatter for success and failure messages
formatter = colorlog.ColoredFormatter(
    "%(yellow)s - %(name)s - %(levelname)s - %(message)s",
    datefmt=None,
    reset=True,
)

# Add the custom formatter to a StreamHandler
handler = colorlog.StreamHandler()
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email="some@email.ua")

    async def log_assertion_result(self, test_name, result, expected=None):
        # Extract only the function name from the fully qualified test name
        test_name_parts = test_name.split("::")  # Split by '::'
        if len(test_name_parts) > 1:
            test_name = test_name_parts[-1]  # Take the last part
        if result == expected:
            test_name = f"{BLUE}{test_name}{RESET}"
            logger.info(
                f"{test_name}: {GREEN}Assertion successful.---> Result matches expected value.{RESET}"
            )
        else:
            logger.error(
                f"{test_name}: {RED}Assertion failed.---> Result does not match expected value.{RESET}"
            )

    @staticmethod
    def async_wrap_assertion_result(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            result = await func(self, *args, **kwargs)
            await self.log_assertion_result(func.__name__, result, *args, **kwargs)
            return result
        return wrapper

    @async_wrap_assertion_result
    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        favorite = True
        q = self.session.query().filter_by()
        if favorite is not None:
            q = q.filter_by()
        q.offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user_id=self.user.id, favorite=favorite, db=self.session)  # type: ignore
        self.assertEqual(result, contacts)

    @async_wrap_assertion_result
    async def test_get_contact_found_by_id(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_id(contact_id=1, user_id=self.user.id, db=self.session)  # type: ignore
        self.assertEqual(result, contact)

    @async_wrap_assertion_result
    async def test_get_contact_found_by_email(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_email(email="as@ee.ua", user_id=self.user.id, db=self.session)  # type: ignore
        self.assertEqual(result, contact)

    @async_wrap_assertion_result
    async def test_get_contact_not_found_by_id(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_contact_by_id(contact_id=1, user_id=self.user.id, db=self.session)  # type: ignore
        self.assertIsNone(result)

    @async_wrap_assertion_result
    async def test_get_contact_not_found_by_email(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_contact_by_email(email="as@ee.ua", user_id=self.user.id, db=self.session)  # type: ignore
        self.assertIsNone(result)

    @async_wrap_assertion_result
    async def test_create_contact(self):
        body = ContactModel(
            first_name="test1",
            last_name="test2",
            email="aa@uu.uu",
            phone="+380 (44) 1234567",
        )
        result = await create(body=body, user_id=self.user.id, db=self.session)  # type: ignore
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.user_id, self.user.id)

    @async_wrap_assertion_result
    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await delete(contact_id=1, user_id=self.user.id, db=self.session)  # type: ignore
        self.assertEqual(result, contact)

    @async_wrap_assertion_result
    async def test_remove_contact_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await delete(contact_id=1, user_id=self.user.id, db=self.session)  # type: ignore
        self.assertIsNone(result)

    @async_wrap_assertion_result
    async def test_update_contact_found(self):
        contact = Contact()
        body = ContactModel(
            first_name="test1-1",
            last_name="test2-1",
            email="aa@uu.uu",
            phone="+380 (44) 1234567",
        )
        self.session.query().filter_by().first.return_value = contact
        self.session.commit.return_value = None
        result = await update(contact_id=1, body=body, user_id=self.user.id, db=self.session)  # type: ignore
        self.assertEqual(result, contact)

    @async_wrap_assertion_result
    async def test_update_contact_not_found(self):
        body = ContactModel(
            first_name="test1-1",
            last_name="test2-1",
            email="aa@uu.uu",
            phone="+380 (44) 1234567",
        )
        self.session.query().filter_by().first.return_value = None
        self.session.commit.return_value = None
        result = await update(contact_id=1, body=body, user_id=self.user.id, db=self.session)  # type: ignore
        self.assertIsNone(result)

    @async_wrap_assertion_result
    async def test_update_favorite_contact_found(self):
        body = ContactFavoriteModel(favorite=True)
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await favorite_update(contact_id=1, body=body, user_id=self.user.id, db=self.session)  # type: ignore
        self.assertEqual(result, contact)

    @async_wrap_assertion_result
    async def test_update_favorite_contact_not_found(self):
        body = ContactFavoriteModel(favorite=True)
        self.session.query().filter_by().first.return_value = None
        result = await favorite_update(contact_id=1, body=body, user_id=self.user.id, db=self.session)  # type: ignore
        self.assertIsNone(result)

    @async_wrap_assertion_result
    async def test_get_contact_search_birthday(self):
        date_now = date.today()
        bd1 = date_now.replace(year=1990) + timedelta(days=2)
        bd2 = date_now.replace(year=2000) + timedelta(days=3)
        bd3 = date_now.replace(year=2010) + timedelta(days=4)
        bd4 = date_now.replace(year=2011) + timedelta(days=25)
        contacts = [
            Contact(birthday=bd1),
            Contact(birthday=bd2),
            Contact(birthday=bd3),
            Contact(birthday=bd4),
        ]
        param = {"days": 7, "skip": 0, "limit": 10}
        query = select().where().order_by()
        self.session.execute(query).scalars.return_value = contacts
        result = await search_birthday(param=param, user_id=self.user.id, db=self.session)  # type: ignore
        self.assertEqual(result, contacts[:-1])

    @async_wrap_assertion_result
    async def test_get_contact_search_birthday_leap(self):
        date_now = date.today()
        bd1 = date(1988, 2, 29)
        contacts = [Contact(birthday=bd1)]
        param = {"days": 7, "skip": 0, "limit": 10, "fixed_now": date(2024, 2, 27)}
        query = select().where().order_by()
        self.session.execute(query).scalars.return_value = contacts
        result = await search_birthday(param=param, user_id=self.user.id, db=self.session)  # type: ignore
        self.assertEqual(result, contacts)


if __name__ == "__main__":
    unittest.main()
