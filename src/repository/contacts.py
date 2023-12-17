from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_, extract

from src.entity.models import Contact
from src.schema.contact import ContactSchema, ContactUpdate


async def get_contacts(limit: int, offset: int, name: str, surname: str, email: str, db: AsyncSession):
    query = select(Contact).offset(offset).limit(limit)

    filters = []
    if name:
        filters.append(Contact.name.ilike(f"%{name}%"))
    if surname:
        filters.append(Contact.surname.ilike(f"%{surname}%"))
    if email:
        filters.append(Contact.email.ilike(f"%{email}%"))

    if filters:
        query = query.where(and_(*filters))

    contacts = await db.execute(query)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    statement = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(statement)
    await db.close()
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession):
    if body.birthday >= date.today():
        raise HTTPException(status_code=400, detail="Birthday must be in the past")

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


async def update_contact(contact_id: int, contact_update: ContactUpdate, db: AsyncSession):
    query = select(Contact).filter_by(id=contact_id)
    result = await db.execute(query)
    existing_contact = result.scalar_one_or_none()

    if not existing_contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact_update.model_dump(exclude_unset=True).items():
        setattr(existing_contact, key, value)

    try:
        await db.commit()
        await db.refresh(existing_contact)
        return existing_contact
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def delete_contact(contact_id: int, db: AsyncSession):
    query = select(Contact).filter_by(id=contact_id)
    result = await db.execute(query)
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    await db.delete(contact)
    try:
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def get_upcoming_birthdays(db: AsyncSession):
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
    return result.scalars().all()
