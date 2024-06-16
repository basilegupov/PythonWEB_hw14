"""
Schemas module.

This module contains Pydantic models for representing data structures used in the application.

Models:
    - ContactSchema: Schema for creating a contact.
    - ContactUpdateSchema: Schema for updating a contact.
    - ContactResponse: Schema for representing a contact response.

"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    """
    Schema for creating a contact.

    Attributes:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (str): The email address of the contact (unique).
        phone_number (str): The phone number of the contact.
        birthday (Date): The birthday of the contact.
        additional_data (str): Additional data related to the contact (nullable).
    """
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone_number: str
    birthday: date
    additional_data: Optional[str] = None


class ContactUpdateSchema(ContactSchema):
    """Schema for updating a contact."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    birthday: Optional[date] = None
    additional_data: Optional[str] = None


class ContactResponse(ContactSchema):
    """
    Schema for representing a contact response.

    Attributes:
        id (int): The unique identifier for the contact.
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (str): The email address of the contact (unique).
        phone_number (str): The phone number of the contact.
        birthday (Date): The birthday of the contact.
        additional_data (str): Additional data related to the contact (nullable).
        created_at (date):  Created at the contact
        updated_at (date): Updated at the contact
        user (UserResponse ): Relationship to the User schema
    """
    id: int
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None
    model_config = ConfigDict(from_attributes=True)
