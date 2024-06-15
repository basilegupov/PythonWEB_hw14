"""
Contacts routes module.

This module defines the endpoints for managing contacts.

Routes:
    - /contacts: Endpoint for retrieving contacts.
    - /contacts/birthdays: Endpoint for retrieving upcoming birthdays.
    - /contacts/{contact_id}: Endpoints for retrieving, updating, and deleting contacts.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       search: str = None, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Endpoint for retrieving contacts.

    Args:
        limit (int): The maximum number of contacts to retrieve.
        offset (int): The offset for pagination.
        search (str): The search query for filtering contacts.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current authenticated user.

    Returns:
        List[ContactResponse]: A list of contact objects.
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, current_user, db, search)
    return contacts


@router.get("/birthdays", response_model=list[ContactResponse])
async def get_upcoming_birthdays_route(db: AsyncSession = Depends(get_db),
                                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Endpoint for retrieving upcoming birthdays.

    Args:
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current authenticated user.

    Returns:
        List[ContactBirthdayResponse]: A list of contact objects with upcoming birthdays.
    """
    print(f"Route {current_user}")
    birthdays = await repositories_contacts.get_upcoming_birthdays(current_user, db)
    return birthdays


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    Endpoint for retrieving a contact by ID.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current authenticated user.

    Returns:
        ContactResponse: The contact object.
    """
    contact = await repositories_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Endpoint for creating a new contact.

    Args:
        body (ContactSchema): The data for creating the contact.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current authenticated user.

    Returns:
        ContactResponse: The created contact object.
    """
    contact = await repositories_contacts.create_contact(body, current_user, db)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Endpoint for updating a contact.

    Args:
        contact_id (int): The ID of the contact to update.
        body (ContactUpdateSchema): The data for updating the contact.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current authenticated user.

    Returns:
        ContactResponse: The updated contact object.
    """
    contact = await repositories_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Endpoint for deleting a contact.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current authenticated user.
    """
    contact = await repositories_contacts.delete_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact
