"""
Database models module containing SQLAlchemy models for the application.

This module defines the database tables and their relationships.

Classes:
    Contact: Represents the 'contacts' table in the database.
    User: Represents the 'users' table in the database.
"""
from datetime import date

from sqlalchemy import Integer, String, Date, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Contact(Base):
    """
    Represents a contact in the database.

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
        user_id (int): The foreign key referencing the user who owns this contact.
        user (relationship): Relationship to the User model.
    """
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String)
    birthday: Mapped[Date] = mapped_column(Date)
    additional_data: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now(),
                                             nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")


class User(Base):
    """
    Represents a user in the database.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user (unique).
        email (str): The email address of the user (unique).
        password (str): The password hash of the user.
        created_at (DateTime): The timestamp when the user was created.
        avatar (str): The avatar image URL of the user (nullable).
        refresh_token (str): The refresh token of the user (nullable).
        created_at (date):  Created timestamp of the user
        updated_at (date): Updated timestamp of the user
        confirmed (bool): Whether the user's email address is confirmed.
    """
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String, nullable=True)
    refresh_token: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
