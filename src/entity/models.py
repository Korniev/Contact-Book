import enum
from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import String, Date, Integer, ForeignKey, DateTime, func, Enum, Boolean


class Base(DeclarativeBase):
    pass


class Contact(Base):
    """
        A SQLAlchemy model representing a contact entity.

        This model stores personal information about contacts associated with a user.

        Attributes:
            id (int): The primary key and unique identifier for the contact.
            name (str): The first name of the contact, up to 150 characters.
            surname (str): The surname of the contact, up to 150 characters.
            email (str): A unique email address of the contact.
            phone (str): The phone number of the contact.
            birthday (date): The date of birth of the contact.

            created_at (DateTime): The timestamp when the contact was created, auto-generated.
            updated_at (DateTime): The timestamp when the contact was last updated, auto-updated.

            user_id (int): Foreign key referencing the 'users' table (nullable).
            user (User): The User object related to the contact (lazy-loaded).
        """
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    surname: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[str] = mapped_column()
    birthday: Mapped[date] = mapped_column(Date)

    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now(),
                                             nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    user: Mapped["User"] = relationship("User", backref='contacts', lazy='joined')


class Role(enum.Enum):
    """
        An enumeration of user roles.

        Defines various roles that can be assigned to users in the system.

        Members:
            admin (str): Represents an admin user.
            moderator (str): Represents a moderator user.
            user (str): Represents a standard user.
        """
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'


class User(Base):
    """
        A SQLAlchemy model representing a user entity.

        This model holds the core details of users in the system, including authentication and role information.

        Attributes:
            id (int): The primary key and unique identifier for the user.
            username (str): The user's chosen username, up to 150 characters.
            email (str): The user's unique email address.
            password (str): The hashed password for the user.
            avatar (str): A URL or path to the user's avatar image (nullable).
            refresh_token (str): A refresh token for the user's session (nullable).

            created_at (DateTime): The timestamp when the user was created, auto-generated.
            updated_at (DateTime): The timestamp when the user was last updated, auto-updated.
            role (Role): The role of the user in the system, with a default value of 'user'.
            confirmed (bool): A boolean flag to indicate if the user's email is confirmed.
        """
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    role: Mapped[Enum] = mapped_column('role', Enum(Role), default=Role.user, nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)