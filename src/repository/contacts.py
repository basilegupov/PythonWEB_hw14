from typing import Optional

# from logger import logger
from datetime import datetime # timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse


async def get_contacts(limit: int, offset: int, user: User, db: AsyncSession, search: Optional[str] = None):
    stmt = select(Contact).filter(Contact.user_id == user.id).offset(offset).limit(limit)
    if search:
        search = f"%{search}%"
        stmt = stmt.filter(
            (Contact.first_name.ilike(search))
            | (Contact.last_name.ilike(search))
            | (Contact.email.ilike(search))
        )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, user: User, db: AsyncSession) -> Optional[Contact]:
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_contact(body: ContactSchema, user: User, db: AsyncSession) -> Contact:
    contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, user: User, db: AsyncSession) -> Optional[Contact]:
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, field, value)
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, user: User, db: AsyncSession) -> Optional[Contact]:
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_upcoming_birthdays(user: User, db: AsyncSession):
    def days_to_birthday(birthday: str):
        if not birthday:
            return None
        today = datetime.now().date()
        birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
        next_birthday = datetime(today.year, birthday.month, birthday.day).date()
        if today > next_birthday:
            next_birthday = datetime(today.year + 1, birthday.month, birthday.day).date()
        return (next_birthday - today).days

    # today = datetime.now().date()
    # end_date = today + timedelta(days=7)
    # logger.info(f"today: {today}, end_date: {end_date}")
    # stmt = select(Contact).filter(
    #     func.date_part('month', Contact.birthday) == today.month,
    #     func.date_part('day', Contact.birthday) >= today.day,
    #     func.date_part('day', Contact.birthday) <= end_date.day
    # )
    stmt = select(Contact).filter(Contact.user_id == user.id)
    contacts = await db.execute(stmt)
    birthdays = contacts.scalars().all()
    upcoming_birthdays = [ContactResponse(
        id=contact.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone_number=contact.phone_number,
        birthday=contact.birthday,
        additional_data=contact.additional_data,
        created_at=contact.created_at,
        updated_at=contact.updated_at,
        user=contact.user
    ) for contact in birthdays if days_to_birthday(str(contact.birthday)) <= 7]
    for contact in upcoming_birthdays:
        print(days_to_birthday(str(contact.birthday)))
    return upcoming_birthdays
