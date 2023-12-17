from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_, extract, cast, Date

from src.entity.models import Contact
from src.schema.contact import ContactSchema, ContactUpdate


async def get_contacts(limit: int, offset: int, name: str, surname: str, email: str, db: AsyncSession):
    statement = select(Contact).offset(offset).limit(limit)
    if name:
        statement = statement.filter(Contact.name.ilike(f"%{name}%"))
    if surname:
        statement = statement.filter(Contact.surname.ilike(f"%{surname}%"))
    if email:
        statement = statement.filter(Contact.email.ilike(f"%{email}%"))

    contacts = await db.execute(statement)
    await db.close()
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    statement = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(statement)
    await db.close()
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession):
    try:
        contact = Contact(**body.model_dump())
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        await db.close()


async def update_contact(contact_id: int, contact: ContactUpdate, db: AsyncSession):
    statement = select(Contact).filter_by(id=contact_id)
    existing_contact = await db.execute(statement)
    existing_contact = existing_contact.scalar_one_or_none()
    if existing_contact:
        for key, value in contact.model_dump().items():
            setattr(existing_contact, key, value)
        await db.commit()
        await db.refresh(existing_contact)
        await db.close()
    return existing_contact


async def delete_contact(contact_id: int, db: AsyncSession):
    statement = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(statement)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
        return contact


async def get_upcoming_birthdays(db: AsyncSession):
    today = date.today()
    next_week = today + timedelta(days=7)

    statement = select(Contact).filter(
        or_(
            and_(
                extract('month', cast(Contact.birthday, Date)) == extract('month', cast(today, Date)),
                extract('day', cast(Contact.birthday, Date)) >= extract('day', cast(today, Date))
            ),
            and_(
                extract('month', cast(Contact.birthday, Date)) == extract('month', cast(next_week, Date)),
                extract('day', cast(Contact.birthday, Date)) <= extract('day', cast(next_week, Date))
            )
        )
    )

    contacts = await db.execute(statement)
    await db.close()
    return contacts.scalars().all()
