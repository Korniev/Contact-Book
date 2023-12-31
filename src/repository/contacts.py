from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_, extract

from src.entity.models import Contact, User
from src.schema import contact
from src.schema.contact import ContactSchema, ContactUpdate


async def get_contacts(limit: int, offset: int, name: str, surname: str, email: str, db: AsyncSession,
                       user: User):
    statement = select(Contact).filter_by(user=user).offset(offset).limit(limit)

    if name:
        statement = statement.filter(Contact.name.ilike(f"%{name}%"))
    if surname:
        statement = statement.filter(Contact.surname.ilike(f"%{surname}%"))
    if email:
        statement = statement.filter(Contact.email.ilike(f"%{email}%"))

    contacts = await db.execute(statement)
    await db.close()
    return contacts.scalars().all()


async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    statement = select(Contact).offset(offset).limit(limit)

    contacts = await db.execute(statement)
    await db.close()
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    statement = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(statement)
    await db.close()
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    if body.birthday >= date.today():
        raise HTTPException(status_code=400, detail="Birthday must be in the past")

    try:
        contact = Contact(**body.model_dump(), user=user)
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        await db.close()


async def update_contact(contact_id: int, contact_update: ContactUpdate, db: AsyncSession, user: User):
    statement = select(Contact).filter_by(id=contact_id, user=user)
    existing_contact = await db.execute(statement)
    existing_contact = existing_contact.scalar_one_or_none()

    if not existing_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if existing_contact:
        for key, value in contact.model_dump().items():
            setattr(existing_contact, key, value)
        await db.commit()
        await db.refresh(existing_contact)
        await db.close()
    return existing_contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    statement = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(statement)
    contact = contact.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if contact:
        await db.delete(contact)
        await db.commit()
        return contact


async def get_upcoming_birthdays(db: AsyncSession, user: User):
    today = date.today()
    next_week = today + timedelta(days=7)

    query = select(Contact).filter(
        or_(
            and_(
                extract('month', Contact.birthday) == today.month,
                extract('day', Contact.birthday) >= today.day,
                extract('month', Contact.birthday) == next_week.month,
                extract('day', Contact.birthday) <= next_week.day,
            ),
            and_(
                today.month != next_week.month,
                or_(
                    and_(
                        extract('month', Contact.birthday) == today.month,
                        extract('day', Contact.birthday) >= today.day,
                    ),
                    and_(
                        extract('month', Contact.birthday) == next_week.month,
                        extract('day', Contact.birthday) <= next_week.day,
                    )
                )
            )
        )
    )

    result = await db.execute(query)
    await db.close()
    return result.scalars().all()
