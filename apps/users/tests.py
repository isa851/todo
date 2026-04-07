from django.test import TestCase
from django.contrib.auth import get_user_model
from core.test_utils import BaseTestCase, TestConstants
from apps.users.models import PhoneNumberValidator

User = get_user_model()


class UserModelTest(BaseTestCase):
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.phone_number, '+996555123456')
        self.assertEqual(self.user.age, 25)
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
    
    def test_user_str_representation(self):
        expected = '@testuser'
        self.assertEqual(str(self.user), expected)
    
    def test_user_full_name_property(self):
        self.assertEqual(self.user.full_name, 'testuser')
        
        self.user.first_name = 'John'
        self.user.save()
        self.assertEqual(self.user.full_name, 'John')
        
        self.user.last_name = 'Doe'
        self.user.save()
        self.assertEqual(self.user.full_name, 'John Doe')
    
    def test_phone_number_validator_valid(self):
        for phone in TestConstants.VALID_PHONE_NUMBERS:
            try:
                PhoneNumberValidator.validate(phone)
            except Exception as e:
                self.fail(f'Valid phone number {phone} raised exception: {e}')
    
    def test_phone_number_validator_invalid(self):
        from django.core.exceptions import ValidationError
        
        for phone in TestConstants.INVALID_PHONE_NUMBERS:
            with self.assertRaises(ValidationError):
                PhoneNumberValidator.validate(phone)
    
    def test_user_manager_create_user(self):
        user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'phone_number': '+996777987654',
            'age': 30
        }
        user = User.objects.create_user(password='newpass123', **user_data)
        
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.phone_number, '+996777987654')
        self.assertEqual(user.age, 30)
        self.assertTrue(user.check_password('newpass123'))
    
    def test_user_manager_create_user_missing_fields(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(password='pass123')
        
        with self.assertRaises(ValueError):
            User.objects.create_user(username='test', password='pass123')
        
        with self.assertRaises(ValueError):
            User.objects.create_user(username='test', email='test@example.com', password='pass123')
    
    def test_user_unique_constraints(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='testuser',
                email='different@example.com',
                phone_number='+996777987654',
                password='pass123'
            )
        
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='differentuser',
                email='test@example.com',
                phone_number='+996777987654',
                password='pass123'
            )
        
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='differentuser',
                email='different@example.com',
                phone_number='+996555123456',
                password='pass123'
            )


class UserModelValidationTest(BaseTestCase):
    
    def test_age_validation(self):
        self.user.age = 25
        self.user.save()
        self.assertEqual(self.user.age, 25)
        
        self.user.age = None
        self.user.save()
        self.assertIsNone(self.user.age)
        
        with self.assertRaises(Exception):
            self.user.age = -1
            self.user.save()
        
        with self.assertRaises(Exception):
            self.user.age = 121
            self.user.save()
    
    def test_email_case_insensitive_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='differentuser',
                email='TEST@EXAMPLE.COM',
                phone_number='+996777987654',
                password='pass123'
            )
    
    def test_username_case_insensitive_lookup(self):
        user = User.objects.get_by_natural_key('TESTUSER')
        self.assertEqual(user, self.user)
