from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schema.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
        Retrieves a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.
            db (AsyncSession): The database session, injected by FastAPI.

        Returns:
            User or None: The User object if found, otherwise None.
        """
    statement = select(User).filter_by(email=email)
    user = await db.execute(statement)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
        Creates a new user in the database.

        The function also attempts to generate a Gravatar URL for the user based on their email.

        Args:
            body (UserSchema): The schema containing the user's data.
            db (AsyncSession): The database session, injected by FastAPI.

        Returns:
            User: The newly created User object.

        Notes:
            If Gravatar generation fails, the avatar attribute is set to None.
        """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
        Updates the refresh token for a given user.

        Args:
            user (User): The User object to update.
            token (str | None): The new refresh token to assign. Can be None to unset the token.
            db (AsyncSession): The database session.

        Notes:
            This function does not return a value but updates the user's refresh token in the database.
        """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
        Marks a user's email as confirmed.

        Args:
            email (str): The email address of the user whose email is to be confirmed.
            db (AsyncSession): The database session.

        Notes:
            This function does not return a value but updates the user's email confirmation status.
        """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
        Updates the avatar URL for a given user.

        Args:
            email (str): The email address of the user whose avatar is to be updated.
            url (str | None): The new avatar URL to assign. Can be None to unset the avatar.
            db (AsyncSession): The database session.

        Returns:
            User: The updated User object with the new avatar URL.
        """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
