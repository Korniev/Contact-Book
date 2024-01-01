from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import contacts as repository_contacts
from src.schema.contact import ContactSchema, ContactUpdate, ContactResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix='/contacts', tags=['contacts'])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get('/', response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=100), offset: int = Query(0, ge=0),
                       name: str = Query(None, title="Name filter"), surname: str = Query(None, title="Surname filter"),
                       email: str = Query(None, title="Email filter"), db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    """
        Retrieves a list of contacts for the current user with optional filters.

        Args:
            limit (int): Maximum number of contacts to return.
            offset (int): Pagination offset.
            name (str): Filter by contact's name.
            surname (str): Filter by contact's surname.
            email (str): Filter by contact's email.
            db (AsyncSession): Database session, injected by FastAPI.
            user (User): Current user, injected by the authentication service.

        Returns:
            list[ContactResponse]: A list of contact details.

        Raises:
            HTTPException: If no contacts are found.
        """
    contacts = await repository_contacts.get_contacts(limit, offset, name, surname, email, db, user)
    if contacts:
        return contacts
    else:
        raise HTTPException(status_code=404, detail="Contacts not found")


@router.get('/all', response_model=list[ContactResponse], dependencies=[Depends(access_to_route_all)])
async def get_all_contacts(limit: int = Query(10, ge=10, le=100), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db)):
    """
        Retrieves all contacts in the database (admin and moderator only).

        Args:
            limit (int), offset (int): Pagination parameters.
            db (AsyncSession): Database session, injected by FastAPI.

        Returns:
            list[ContactResponse]: A list of all contacts.

        Raises:
            HTTPException: If no contacts are found.
            :param db:
            :param limit:
            :param offset:
        """
    contacts = await repository_contacts.get_all_contacts(limit, offset, db)
    if contacts:
        return contacts
    else:
        raise HTTPException(status_code=404, detail="Contacts not found")


@router.get('/{contacts_id}', response_model=ContactResponse)
async def get_contact(contacts_id: int, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
        Retrieves a specific contact by ID.

        Args:
            contacts_id (int): The unique identifier of the contact.
            db (AsyncSession): Database session, injected by FastAPI.
            user (User): Current user, injected by the authentication service.

        Returns:
            ContactResponse: Detailed information about the contact.

        Raises:
            HTTPException: If the contact is not found.
        """
    contact = await repository_contacts.get_contact(contacts_id, db, user)
    if contact:
        return contact
    else:
        raise HTTPException(status_code=404, detail="Contact not found")


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
        Creates a new contact for the current user.

        Args:
            body (ContactSchema): The data for creating a new contact.
            db (AsyncSession), user (User): Injected by FastAPI.

        Returns:
            ContactResponse: The created contact's details.
            :param db:
            :param body:
            :param user:
        """
    contact = await repository_contacts.create_contact(body, db, user)
    return contact


@router.put('/{contacts_id}', response_model=ContactResponse, status_code=status.HTTP_200_OK)
async def update_contact(contacts_id: int, body: ContactUpdate, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
        Updates a contact's details by ID.

        Args:
            contacts_id (int): The ID of the contact to update.
            body (ContactUpdate): The updated contact data.
            db (AsyncSession), user (User): Injected by FastAPI.

        Returns:
            ContactResponse: The updated contact's details.

        Raises:
            HTTPException: If the contact is not found.
            :param db:
            :param contacts_id:
            :param body:
            :param user:
        """
    contact = await repository_contacts.update_contact(contacts_id, body, db, user)
    if contact:
        return contact
    else:
        raise HTTPException(status_code=404, detail="Contact not found")


@router.delete('/{contacts_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contacts_id: int, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
        Deletes a contact by ID.

        Args:
            contacts_id (int): The ID of the contact to delete.
            db (AsyncSession), user (User): Injected by FastAPI.

        Returns:
            None: A confirmation of deletion.

        Raises:
            HTTPException: If the contact is not found.
            :param db:
            :param contacts_id:
            :param user:
        """
    contact = await repository_contacts.delete_contact(contacts_id, db, user)
    if contact:
        return contact
    else:
        raise HTTPException(status_code=404, detail="Contact not found")


@router.get("/birthday/", response_model=list[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    """
        Retrieves contacts with upcoming birthdays within the next week.

        Args:
            db (AsyncSession), user (User): Injected by FastAPI.

        Returns:
            list[ContactResponse]: Contacts with upcoming birthdays.

        Raises:
            HTTPException: If no contacts with upcoming birthdays are found.
            :param db:
            :param user:
        """
    contacts = await repository_contacts.get_upcoming_birthdays(db, user)
    if contacts:
        return contacts
    else:
        raise HTTPException(status_code=404, detail="Contacts not found")
