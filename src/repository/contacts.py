from typing import Optional

# from logger import logger
from datetime import datetime  # timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse


async def get_contacts(limit: int, offset: int, user: User, db: AsyncSession, search: Optional[str] = None):
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param offset: The number of contacts to skip.
    :type offset: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :param search: Optional search string to filter contacts by first name, last name, or email.
    :type search: Optional[str]
    :return: A list of contacts.
    :rtype: List[Contact]
    """
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
    """
    Retrieves a specific contact for a user by contact ID.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The contact if found, otherwise None.
    :rtype: Optional[Contact]
    """
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_contact(body: ContactSchema, user: User, db: AsyncSession) -> Contact:
    """
    Creates a new contact for a user.

    :param body: The contact data.
    :type body: ContactSchema
    :param user: The user to create the contact for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The created contact.
    :rtype: Contact
    """
    contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, user: User, db: AsyncSession) -> Optional[Contact]:
    """
    Updates an existing contact for a user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated contact data.
    :type body: ContactUpdateSchema
    :param user: The user to update the contact for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated contact if found, otherwise None.
    :rtype: Optional[Contact]
    """
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
    """
    Deletes a specific contact for a user by contact ID.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param user: The user to delete the contact for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The deleted contact if found, otherwise None.
    :rtype: Optional[Contact]
    """
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_upcoming_birthdays(user: User, db: AsyncSession):
    """
    Retrieves a list of contacts with upcoming birthdays within the next 7 days for a specific user.

    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: A list of contacts with upcoming birthdays.
    :rtype: List[Contact]
    """

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
