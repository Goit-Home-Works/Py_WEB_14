"""
Module Description:
This module contains API routes and functions related to authentication and user management.

Functions:
- signup: Asynchronously creates a new user account and sends a confirmation email.
- login: Asynchronously validates user credentials and generates access and refresh tokens.
- get_current_user: Asynchronously retrieves the current authenticated user.
- refresh_access_token: Asynchronously refreshes the access token using the refresh token.
- refresh_token: Asynchronously refreshes the access and refresh tokens.
- confirmed_email: Asynchronously confirms a user's email address.
- request_email: Asynchronously sends a confirmation email for email verification.

Dependencies:
- fastapi.APIRouter: Router for API endpoints grouping.
- fastapi.Depends: Dependency injection mechanism for FastAPI.
- fastapi.HTTPException: Exception class for HTTP errors in FastAPI.
- fastapi.Request: Represents an HTTP request in FastAPI.
- fastapi.Response: Represents an HTTP response in FastAPI.
- fastapi.status: HTTP status codes in FastAPI.
- fastapi.Query: Query parameters in FastAPI.
- fastapi.Security: Security utilities for FastAPI.
- fastapi.BackgroundTasks: Background tasks execution in FastAPI.
- fastapi.security.HTTPBearer: HTTP Bearer token security scheme in FastAPI.
- fastapi.security.HTTPAuthorizationCredentials: Represents HTTP authorization credentials in FastAPI.
- fastapi.security.OAuth2PasswordRequestForm: Represents OAuth2 password request form in FastAPI.
- sqlalchemy.orm.Session: SQLAlchemy database session for database operations.
- logging: Standard Python logging module for logging messages.
- config.config.settings: Configuration settings for the application.
- schemas.user.UserModel: User model schema for creating and updating user information.
- schemas.user.UserResponse: User response model schema.
- schemas.user.UserDetailResponse: Detailed user response model schema.
- schemas.auth.AccessTokenRefreshResponse: Access token refresh response model schema.
- schemas.auth.RequestEmail: Request email model schema.
- repository.auth: Repository module for authentication operations.
- repository.users: Repository module for user-related operations.
- services.auth.auth_service: Authentication service for token generation and validation.
- services.emails.send_email: Asynchronously sends an email.
"""

from typing import Annotated, Any, List
import logging
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    Query,
    Security,
    status,
    Cookie,
    BackgroundTasks,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasicCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from sqlalchemy.orm import Session

from config.config import settings
from db.database import get_db
from db.models import User
from schemas.user import UserResponse, UserDetailResponse, UserModel
from services.auth import auth_service
from repository import auth as repository_auth
from repository import users as repository_users
from schemas.auth import AccessTokenRefreshResponse
from services.emails import send_email

from schemas.auth import RequestEmail

logger = logging.getLogger(f"{settings.app_name}.{__name__}")

router = APIRouter(prefix="", tags=["Auth"])

security = HTTPBearer()

SET_COOKIES = False


@router.post(
    "/signup",
    response_model=UserDetailResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    body: UserModel,
    bt: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """
    Sign up a new user with the provided user information.

    Parameters:
    - body (UserModel): The user data to be used for signup.
    - bt (BackgroundTasks): Background tasks to be executed.
    - request (Request): The HTTP request object.
    - db (Session): The database session.

    Returns:
    - dict: A dictionary containing the new user details and a success message.

    Raises:
    - HTTPException: If the user account already exists.

    This function creates a new user account, saves it to the database, and sends a confirmation email.
    If the user account already exists, it raises an HTTPException with a 409 Conflict status code.
    """
    new_user = await repository_auth.signup(body=body, db=db)
    print(f"New user details: id={new_user.id}, username={new_user.username}, email={new_user.email}, avatar={new_user.avatar}, role={new_user.role}")
    if new_user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    bt.add_task(
        send_email, str(new_user.email), str(new_user.username), str(request.base_url)
    )

    return {
        "user": new_user,
        "detail": "User successfully created. Check your email for confirmation.",
    }


@router.post("/login", response_model=AccessTokenRefreshResponse)
async def login(
    response: Response,
    body: Annotated[auth_service.auth_response_model, Depends()],  # type: ignore
    db: Session = Depends(get_db),
) -> dict:
    """
    Log in a user with the provided credentials.

    Parameters:
    - response (Response): The HTTP response object.
    - body (Annotated[auth_service.auth_response_model, Depends()]): The user credentials.
    - db (Session): The database session.

    Returns:
    - dict: A dictionary containing the access and refresh tokens.

    Raises:
    - HTTPException: If the credentials are invalid or the user is not confirmed.

    This function validates the user credentials, generates access and refresh tokens, and sets them as cookies.
    If the credentials are invalid or the user is not confirmed, it raises an HTTPException with a 401 Unauthorized status code.
    """
    print(f"{body.username=}")
    user = await repository_users.get_user_by_email(body.username, db)
    print(f"{user.confirmed=}")
    if user is None:
        exception_data = {
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "detail": "Invalid credentianal",
        }
        raise HTTPException(**exception_data)
    if not bool(user.confirmed):
        exception_data = {
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "detail": "Not confirmed",
        }
        raise HTTPException(**exception_data)

    token = repository_auth.login(user=user, password=body.password, db=db)
    print(f"{token=}")
    if token is None:
        exception_data = {
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "detail": "Invalid credentianal",
        }
        if SET_COOKIES:
            response.delete_cookie(key="access_token", httponly=True, path="/api/")
            exception_data.update(
                {
                    "headers": {
                        "set-cookie": response.headers.get("set-cookie", ""),
                    }
                }
            )
        raise HTTPException(**exception_data)

    refresh_token = token.get("refresh_token")
    if refresh_token:
        await repository_auth.update_refresh_token(
            username=body.username, refresh_token=refresh_token, db=db
        )
    new_access_token = token.get("access_token")
    if SET_COOKIES:
        if new_access_token:
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                path="/api/",
                expires=token.get("expire_access_token"),
            )
        else:
            response.delete_cookie(key="access_token", httponly=True, path="/api/")
        if new_access_token:
            print(f"{token.get('expire_refresh_token')=}")
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,  # type: ignore
                httponly=True,
                path="/api/",
                expires=token.get("expire_refresh_token"),
            )
        else:
            response.delete_cookie(key="refresh_token", httponly=True, path="/api/")
    print("login: ", token)
    return token


async def get_current_user(
    response: Response,
    access_token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
    token: str | None = Depends(repository_auth.auth_service.auth_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Retrieve the current authenticated user based on the provided tokens.

    Parameters:
    - response (Response): The HTTP response object.
    - access_token (Annotated[str | None, Cookie()]): The access token from the cookie.
    - refresh_token (Annotated[str | None, Cookie()]): The refresh token from the cookie.
    - token (str | None): The token from the Authorization header.
    - db (Session): The database session.

    Returns:
    - User | None: The authenticated user object if found, otherwise None.

    Raises:
    - HTTPException: If the credentials could not be validated.

    This function retrieves the current authenticated user by validating the provided tokens.
    If the tokens are not valid or could not be found, it raises an HTTPException with a 401 Unauthorized status code.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer",
            "set-cookie": response.headers.get("set-cookie", ""),
        },
    )
    user = None
    new_access_token = None
    print(f"{access_token=}, {refresh_token=}, {token=}")
    if not token:
        print("used cookie access_token")
        token = access_token
    if token:
        user = await repository_auth.a_get_current_user(token, db)
        if not user and token != access_token:
            user = await repository_auth.a_get_current_user(access_token, db)
        if not user and refresh_token:
            result = await refresh_access_token(refresh_token)
            print(f"refresh_access_token  {result=}")
            if result:
                new_access_token = result.get("access_token")
                email = result.get("email")
                user = await repository_users.get_user_by_email(str(email), db)
                if SET_COOKIES:
                    if new_access_token:
                        response.set_cookie(
                            key="access_token",
                            value=new_access_token,
                            httponly=True,
                            path="/api/",
                            expires=result.get("expire_token"),
                        )
                    else:
                        response.delete_cookie(
                            key="access_token", httponly=True, path="/api/"
                        )
    if user is None:
        raise credentials_exception
    return user


@router.get("/secret")
async def read_item(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """
    Retrieves information about the authenticated user for accessing the secret router.

    Parameters:
    - current_user (User): The current authenticated user object.

    Returns:
    - dict[str, Any]: A dictionary containing information about the secret router, including the owner's email.
    """
    auth_result = {"email": current_user.email}
    return {"message": "secret router", "owner": auth_result}


async def refresh_access_token(refresh_token: str) -> dict[str, Any] | None:

    """
    Refreshes the access token based on the provided refresh token.

    Parameters:
    - refresh_token (str): The refresh token.

    Returns:
    - dict[str, Any] | None: A dictionary containing the new access token and its expiration time if successful, otherwise None.
    """
    if refresh_token:
        email = auth_service.decode_refresh_token(refresh_token)
        access_token, expire_token = auth_service.create_access_token(
            data={"sub": email}
        )
        return {
            "access_token": access_token,
            "expire_token": expire_token,
            "email": email,
        }
    return None


@router.get("/refresh_token")
async def refresh_token(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Refreshes the access token using the refresh token.

    Parameters:
    - response (Response): The HTTP response object.
    - refresh_token (Annotated[str | None, Cookie()]): The refresh token from the cookie.
    - credentials (HTTPAuthorizationCredentials): The HTTP Authorization credentials.
    - db (Session): The database session.

    Returns:
    - dict[str, Any]: A dictionary containing the new access token, its expiration time, and other token information.

    Raises:
    - HTTPException: If the refresh token is invalid or expired.
    """

    token: str = credentials.credentials
    logger.info(f"refresh_token {token=}")
    if not token and refresh_token:
        token = refresh_token
    email = auth_service.decode_refresh_token(token)
    logger.info(f"refresh_token {email=}")
    user: User | None = await repository_users.get_user_by_email(email, db)
    if user and user.refresh_token != token:  # type: ignore
        await repository_users.update_user_refresh_token(user, None, db)
        response.delete_cookie(key="refresh_token", httponly=True, path="/api/")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={
                "set-cookie": response.headers.get("set-cookie", ""),
            },
        )
    new_access_token, expire_access_token = auth_service.create_access_token(
        data={"sub": email}
    )
    new_refresh_token, expire_refresh_token = auth_service.create_refresh_token(
        data={"sub": email}
    )
    await repository_users.update_user_refresh_token(user, new_refresh_token, db)
    if SET_COOKIES:
        if new_access_token:
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                path="/api/",
                expires=expire_access_token,
            )
        else:
            response.delete_cookie(key="access_token", httponly=True, path="/api/")
        if new_access_token:
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                httponly=True,
                path="/api/",
                expires=expire_refresh_token,
            )
        else:
            response.delete_cookie(key="refresh_token", httponly=True, path="/api/")
    return {
        "access_token": new_access_token,
        "expire_access_token": expire_access_token,
        "refresh_token": new_refresh_token,
        "expire_refresh_token": expire_refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Confirms the user's email based on the provided token.

    Parameters:
    - token (str): The verification token.
    - db (Session): The database session.

    Returns:
    - dict[str, str]: A dictionary containing a message indicating the email confirmation status.
    """

    email = auth_service.get_email_from_token(token)
    if email:
        user = await repository_users.get_user_by_email(email, db)
        if user:
            if bool(user.confirmed):
                return {"message": "Your email is already confirmed"}
            await repository_users.confirmed_email(email, db)
            return {"message": "Email confirmed"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
    )


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Requests email confirmation for the user.

    Parameters:
    - body (RequestEmail): The request body containing the user's email.
    - background_tasks (BackgroundTasks): The background tasks for sending emails.
    - request (Request): The HTTP request object.
    - db (Session): The database session.

    Returns:
    - dict[str, str]: A dictionary containing a message indicating the email confirmation status.
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        if bool(user.confirmed):
            return {"message": "Your email is already confirmed"}
        background_tasks.add_task(
            send_email, str(user.email), str(user.username), str(request.base_url)
        )
    return {"message": "Check your email for confirmation."}
