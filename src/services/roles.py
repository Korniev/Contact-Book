from fastapi import Request, Depends, HTTPException, status

from src.entity.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    """
        A FastAPI dependency class for role-based access control.

        This class is used to restrict access to certain API routes based on the user's role.

        Attributes:
            allowed_roles (list[Role]): A list of roles that are allowed to access the route.
        """
    def __init__(self, allowed_roles: list[Role]):
        """
            Initializes the RoleAccess class with allowed roles.

            Args:
                allowed_roles (list[Role]): A list of `Role` enum values representing the roles allowed to access certain routes.
            """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
            The callable method for the dependency, invoked automatically by FastAPI.

            Checks if the current user's role is in the list of allowed roles for the route.
            If not, it raises an HTTP 403 Forbidden exception.

            Args:
                request (Request): The incoming HTTP request.
                user (User): The current authenticated user, obtained from the authentication service.

            Raises:
                HTTPException: A 403 Forbidden error if the user's role is not in the allowed roles.
            """
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN"
            )