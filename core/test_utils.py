"""
Base test utilities and fixtures for the Todo app project
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from PIL import Image
import io
import tempfile

User = get_user_model()


class BaseTestCase(TestCase):
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_number': '+996555123456',
            'age': 25,
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
        
    def create_todo(self, title='Test Todo', description='Test Description', is_completed=False):
        from apps.todo.models import Todo
        return Todo.objects.create(
            title=title,
            description=description,
            is_completed=is_completed,
            owner=self.user
        )
    
    def create_image_file(self, name='test.jpg', size=(100, 100), color=(255, 0, 0)):
        image = Image.new('RGB', size, color)
        image_io = io.BytesIO()
        image.save(image_io, 'JPEG')
        image_io.seek(0)
        return image_io


class BaseAPITestCase(APITestCase):
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_number': '+996555123456',
            'age': 25,
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)
        
    def authenticate_user(self, user=None):
        if user is None:
            user = self.user
        self.client.force_authenticate(user=user)
        
    def create_todo(self, title='Test Todo', description='Test Description', is_completed=False):
        from apps.todo.models import Todo
        return Todo.objects.create(
            title=title,
            description=description,
            is_completed=is_completed,
            owner=self.user
        )


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'phone_number': '+996555123456',
        'age': 25,
        'password': 'testpass123'
    }


@pytest.fixture
def user_instance(user_data):
    return User.objects.create_user(**user_data)


@pytest.fixture
def todo_data():
    return {
        'title': 'Test Todo',
        'description': 'Test Description',
        'is_completed': False
    }


@pytest.fixture
def todo_instance(user_instance, todo_data):
    """Fixture providing a todo instance"""
    from apps.todo.models import Todo
    return Todo.objects.create(owner=user_instance, **todo_data)


@pytest.fixture
def image_file():
    """Fixture providing a test image file"""
    image = Image.new('RGB', (100, 100), color='red')
    image_io = io.BytesIO()
    image.save(image_io, 'JPEG')
    image_io.seek(0)
    return image_io


class TestConstants:
    """Test constants for reuse across tests"""
    
    VALID_PHONE_NUMBERS = [
        '+996555123456',
        '+996777987654',
        '+996222111333'
    ]
    
    INVALID_PHONE_NUMBERS = [
        '996555123456',  
        '+99655512345',  
        '+9965551234567',  
        '+99655512345a',  
        '+796555123456',  
    ]
    
    VALID_EMAILS = [
        'test@example.com',
        'user.name@domain.co.uk',
        'user+tag@example.org'
    ]
    
    INVALID_EMAILS = [
        'invalid-email',
        '@domain.com',
        'user@',
        'user..name@domain.com'
    ]
