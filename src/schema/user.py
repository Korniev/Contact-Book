from pydantic import BaseModel, EmailStr, Field

from src.entity.models import Role


class UserSchema(BaseModel):
    """
        Pydantic model for user registration and creation.

        Attributes:
            username (str): The user's chosen username. Minimum length of 3 and maximum length of 50 characters.
            email (EmailStr): The user's email address, validated as an email string.
            password (str): The user's password. Minimum length of 6 and maximum length of 8 characters.
        """
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    """
        Pydantic model for returning user information in API responses.

        Attributes:
            id (int): The unique identifier of the user.
            username (str): The user's username.
            email (EmailStr): The user's email address.
            avatar (str): URL or path to the user's avatar image.
            role (Role | str | None): The role assigned to the user. Can be a `Role` enum, string, or None.

        Config:
            from_attributes: A Pydantic configuration attribute for custom behaviors.
        """
    id: int = 1
    username: str
    email: EmailStr
    avatar: str
    role: Role | str | None

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    """
        Pydantic model for JWT token data in authentication responses.

        Attributes:
            access_token (str): The JWT access token.
            refresh_token (str): The JWT refresh token.
            token_type (str): The type of the token, defaulting to 'bearer'.
        """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
        Pydantic model for requesting operations based on a user's email.

        Attributes:
            email (EmailStr): The user's email address, used for operations like email verification requests.
        """
    email: EmailStr
