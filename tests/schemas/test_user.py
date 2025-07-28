import unittest
from pydantic import ValidationError
from backend.app.schemas.user import User, Update_user, Login

class TestUserSchema(unittest.TestCase):

    def test_valid_user(self):
        user = User(
            name="john doe",
            email="John.DOE@Email.com",
            phone_no=9876543210,
            password="Password@123"
        )
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.email, "john.doe@email.com")

    def test_invalid_name_too_short(self):
        with self.assertRaises(ValidationError) as context:
            User(name="Al", email="a@a.com", phone_no=1234567890, password="Password@123")
        self.assertIn("Name should be at least 3 charecters", str(context.exception))

    def test_invalid_phone_number(self):
        with self.assertRaises(ValidationError) as context:
            User(name="Alex", email="a@a.com", phone_no=123, password="Password@123")
        self.assertIn("Phone number must be a 10-digit integer", str(context.exception))

    def test_invalid_password(self):
        with self.assertRaises(ValidationError) as context:
            User(name="Alex", email="a@a.com", phone_no=9876543210, password="weakpass")
        self.assertIn("Password must be at least 8 characters long", str(context.exception))

class TestUpdateUserSchema(unittest.TestCase):

    def test_valid_update_user(self):
        update = Update_user(name="john doe", phone_no=9998887776)
        self.assertEqual(update.name, "John Doe")
        self.assertEqual(update.phone_no, 9998887776)

    def test_update_user_invalid_name(self):
        with self.assertRaises(ValidationError) as context:
            Update_user(name="Al", phone_no=9998887776)
        self.assertIn("Name should be at least 3 charecters", str(context.exception))

    def test_update_user_invalid_phone(self):
        with self.assertRaises(ValidationError) as context:
            Update_user(name="Alice", phone_no=999)
        self.assertIn("Phone number must be a 10-digit integer", str(context.exception))

class TestLoginSchema(unittest.TestCase):

    def test_valid_login(self):
        login = Login(email="test@DOMAIN.com", password="StrongPass1!")
        self.assertEqual(login.email, "test@domain.com")

    def test_invalid_login_password(self):
        with self.assertRaises(ValidationError) as context:
            Login(email="test@domain.com", password="123")
        self.assertIn("Password must be at least 8 characters long", str(context.exception))

