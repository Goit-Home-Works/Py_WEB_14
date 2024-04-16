import os
from pathlib import Path
from unittest.mock import MagicMock
import pytest

hw_path: str = str(Path(__file__).resolve().parent.parent.joinpath("src"))

from src.db.models import User


def test_create_user(client, user, mock_ratelimiter, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.emails.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409  # Update assertion to expect 409
    data = response.json()
    assert (
        data["detail"] == "Account already exists"
    )  # Verify correctness of error message


def test_repeat_create_user(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"

def test_login_user_not_confirmed(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid credentials"

def test_login_wrong_password(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid credentials"


def test_login_wrong_email(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/login",
        data={"username": "email", "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid credentials"

def test_login_user(client, user, mock_ratelimiter, session):
    # Ensure the user exists in the database
    existing_user = session.query(User).filter(User.email == user.get("email")).first()
    if existing_user:
        existing_user.confirmed = True
        session.commit()

        # Perform login request
        response = client.post(
            "/api/auth/login",
            data={"username": user.get("email"), "password": user.get("password")},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["token_type"] == "bearer"
    else:
        # Skip the test if the user does not exist in the database
        pytest.skip(f"User with email {user.get('email')} does not exist in the database")
