# from your_module import get_upcoming_birthdays, Contact, ContactResponse, User  # замените your_module на имя вашего модуля
# from unittest.mock import AsyncMock, patch, MagicMock
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

    async def test_get_upcoming_birthdays(self):
        # Создаем фиктивные данные
        fake_today = datetime(2024, 6, 16).date()
        fake_birthday_1 = fake_today + timedelta(days=3)  # День рождения через 3 дня
        # День рождения через 10 дней
        fake_birthday_2 = fake_today + timedelta(days=10)

        contact_1 = Contact(
            id=1, first_name="John", last_name="Doe", email="john@example.com", phone_number="1234567890",
            birthday=fake_birthday_1, additional_data="", created_at=fake_today, updated_at=fake_today, user=None
        )
        contact_2 = Contact(
            id=2, first_name="Jane", last_name="Doe", email="jane@example.com", phone_number="0987654321",
            birthday=fake_birthday_2, additional_data="", created_at=fake_today, updated_at=fake_today, user=None
        )

        self.session.execute.return_value = [
            contact_1, contact_2]

        result = await get_upcoming_birthdays(self.user, self.session)

        # Проверка результатов
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].first_name, "John")
        self.assertEqual(result[0].last_name, "Doe")
        self.assertEqual(result[0].email, "john@example.com")


# Запуск тестов

if __name__ == '__main__':
    unittest.main()
