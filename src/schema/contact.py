from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr

from src.schema.user import UserResponse


class ContactSchema(BaseModel):
    """
        Pydantic model for creating a new contact.

        Attributes:
            name (str): The contact's first name, with a maximum length of 150 characters.
            surname (str): The contact's surname, with a maximum length of 150 characters.
            email (EmailStr): The contact's email address, validated as an email string.
            phone (str): The contact's phone number.
            birthday (date): The contact's date of birth.
        """
    name: str = Field(max_length=150)
    surname: str = Field(max_length=150)
    email: EmailStr
    phone: str
    birthday: date


class ContactUpdate(BaseModel):
    """
        Pydantic model for updating existing contact details.

        Attributes:
            name (str): The contact's updated first name.
            surname (str): The contact's updated surname.
            email (EmailStr): The contact's updated email address.
            phone (str): The contact's updated phone number.
            birthday (date): The contact's updated date of birth.
        """
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date


class ContactResponse(BaseModel):
    """
        Pydantic model for returning contact information in API responses.

        Attributes:
            id (int): The unique identifier of the contact.
            name (str): The contact's first name.
            surname (str): The contact's surname.
            email (EmailStr): The contact's email address.
            phone (str): The contact's phone number.
            birthday (date): The contact's date of birth.
            created_at (datetime | None): The timestamp when the contact was created. None if not available.
            updated_at (datetime | None): The timestamp when the contact was last updated. None if not available.
            user (UserResponse | None): The user associated with this contact. None if not associated with a user.

        Config:
            from_attributes: A Pydantic configuration attribute for custom behaviors.
        """
    id: int = 1
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None

    class Config:
        from_attributes = True