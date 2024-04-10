from typing import Any, List
import logging

from fastapi import Depends, HTTPException, status, Request

from db.models import Role, User
from routes import auth
from config.config import settings

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


class RoleAccess:
    """
    Middleware class to restrict access based on user roles.

    Attributes:
    - allowed_roles (List[Role]): List of roles allowed to access the endpoint.
    """

    def __init__(self, allowed_roles: List[Role]) -> None:
        """
        Initializes the RoleAccess middleware with the allowed roles.

        Parameters:
        - allowed_roles (List[Role]): List of roles allowed to access the endpoint.
        """
        self.allowed_roles = allowed_roles

    async def __call__(
        self, request: Request, current_user: User = Depends(auth.get_current_user)
    ) -> Any:
        """
        Callable method to check user's role against allowed roles.

        Parameters:
        - request (Request): The incoming request object.
        - current_user (User): The authenticated user obtained from the authentication middleware.

        Raises:
        - HTTPException: If the user's role is not allowed to access the endpoint.

        Returns:
        - Any: Returns None if the user's role is allowed, otherwise raises HTTPException.
        """
        logger.debug(f"{request.method=}, {request.url=}")
        if current_user:
            logger.debug(f"User role: {current_user.role}")
            logger.debug(f"Allower roles: {self.allowed_roles}")
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Operation frobidden"
            )
