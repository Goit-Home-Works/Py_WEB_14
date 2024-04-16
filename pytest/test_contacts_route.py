from datetime import datetime
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

hw_path: str = str(Path(__file__).resolve().parent.parent.joinpath("src"))

from src.db.models import User
from src.repository.users import create_user


# class MockRedis:
#     async def get_connection(self, *args):
#         print("MockRedis get_connection")
#         return MockRedis
#
#     async def get(self, *args):
#         print("MockRedis get")
#         return None
#
#     async def set(self, *args):
#         print("MockRedis set")
#         return None
#
#     async def expire(self, *args):
#         print("MockRedis expire")
#         return None
#
#     async def release(self, *args):
#         print("MockRedis release")
#         return None


def create_user_if_not_exists(client, session, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.emails.send_email", mock_send_email)

    # Check if the user already exists
    existing_user = session.query(User).filter(User.email == user.get("email")).first()
    if existing_user:
        return  # User already exists, no need to create again

    # User doesn't exist, create it
    response = client.post(
        "/api/auth/signup",
        json={"username": user["email"], **user},  # Include the "username" field
    )
    assert response.status_code == 201, response.text

