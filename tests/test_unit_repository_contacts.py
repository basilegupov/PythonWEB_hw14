import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    update_contact,
    delete_contact,
    get_upcoming_birthdays,
)
from src.entity.models import User, Contact
from src.schemas.contact import ContactSchema, ContactUpdateSchema


class TestContactRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username="test", password="test", email="test@test.com")
        self.session = AsyncMock(spec=AsyncSession)
        self.contact = Contact(id=1, user_id=self.user.id, first_name="Test", last_name="Contact",
                               email="test@example.com")

    async def test_get_contacts(self):
        # Test parameters
        limit = 10
        offset = 0
        # Mocking the database query result
        contacts = [Contact(id=1, first_name="Test", last_name="Test", email="test@example.com", user_id=1),
                    Contact(id=2, first_name="Test_2", last_name="Test_2", email="test_2@example.com", user_id=1)]
        mock_contacts = MagicMock()
        mock_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mock_contacts
        # Calling the function under test
        result = await get_contacts(limit, offset, self.user, self.session)
        # Verifying the result
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        # Test parameters
        body = ContactSchema(first_name="John", last_name="Doe", email="john@example.com", phone_number="1234567890",
                             birthday="1990-01-01")
        # Calling the function under test
        result = await create_contact(body, self.user, self.session)
        # Verifying that the contact is created
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        # self.assertEqual(result.phone_number, body.phone_number)
        # self.assertEqual(result.birthday, body.birthday)

    async def test_update_contact(self):
        # Test parameters
        body = ContactUpdateSchema(first_name="John")
        # Mocking the database query result
        mock_contact = MagicMock()
        mock_contact.scalar_one_or_none.return_value = Contact(id=1, first_name="John", email="john@example.com",
                                                               user_id=self.user.id)
        self.session.execute.return_value = mock_contact
        # Calling the function under test
        result = await update_contact(1, body, self.user, self.session)
        # Verifying that the contact is updated
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)

    async def test_delete_contact(self):

        # Mocking the database query result
        mock_contact = MagicMock()
        mock_contact.scalar_one_or_none.return_value = self.contact
        self.session.execute.return_value = mock_contact
        # Calling the function under test
        result = await delete_contact(self.contact.id, self.user, self.session)
        # Verifying that the contact is deleted
        self.assertEqual(result, self.contact)

    # async def test_get_upcoming_birthdays(self):
    #     # Mocking the database query result
    #     today = datetime.now().date()
    #     contacts = [
    #         Contact(birthday=today + timedelta(days=i), user_id=self.user.id) for i in range(5)
    #     ]
    #     mock_contact = MagicMock()
    #     mock_contact.return_value.scalars.all.return_value = contacts
    #     self.session.execute.return_value = mock_contact
    #
    #     # Calling the function under test
    #     result = await get_upcoming_birthdays(self.user, self.session)
    #     # Verifying that the correct contacts with upcoming birthdays are returned
    #     expected_contacts = contacts[:7]  # Get contacts with birthdays within the next 7 days
    #     self.assertEqual(result, expected_contacts)
    async def test_get_upcoming_birthdays(self):
        # Mocking the database session
        session = MagicMock(spec=AsyncSession)
        # Test parameters
        user = User(id=1)
        # Mocking the database query result
        today = datetime.now().date()
        contacts = [
            Contact(birthday=today + timedelta(days=i), user_id=user.id) for i in range(5)
        ]
        mock_result = MagicMock()
        mock_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=contacts)))
        session.execute = AsyncMock(return_value=mock_result)
        # Calling the function under test
        result = await get_upcoming_birthdays(user, session)
        # Verifying that the correct contacts with upcoming birthdays are returned
        expected_contacts = contacts[:7]  # Get contacts with birthdays within the next 7 days
        self.assertEqual(result, expected_contacts)


if __name__ == '__main__':
    unittest.main()
