from django.test import TestCase
from django.contrib.auth import get_user_model
from core.test_utils import BaseTestCase
from apps.todo.models import Todo

User = get_user_model()


class TodoModelTest(BaseTestCase):
    
    def test_todo_creation(self):
        todo = self.create_todo()
        
        self.assertEqual(todo.title, 'Test Todo')
        self.assertEqual(todo.description, 'Test Description')
        self.assertFalse(todo.is_completed)
        self.assertEqual(todo.owner, self.user)
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)
        self.assertIsNone(todo.completed_at)
    
    def test_todo_str_representation(self):
        todo = self.create_todo()
        expected = 'Test Todo - testuser'
        self.assertEqual(str(todo), expected)
    
    def test_todo_status_display_property(self):
        todo = self.create_todo()
        self.assertEqual(todo.status_display, 'Pending')
        
        todo.is_completed = True
        todo.save()
        self.assertEqual(todo.status_display, 'Completed')
    
    def test_todo_save_completion_timestamp(self):
        todo = self.create_todo()
        
        self.assertIsNone(todo.completed_at)
        
        todo.is_completed = True
        todo.save()
        self.assertIsNotNone(todo.completed_at)
        
        todo.is_completed = False
        todo.save()
        self.assertIsNone(todo.completed_at)
    
    def test_todo_manager_methods(self):
        completed_todo = self.create_todo(title='Completed', is_completed=True)
        pending_todo = self.create_todo(title='Pending', is_completed=False)
        
        user_todos = Todo.objects.for_user(self.user)
        self.assertEqual(user_todos.count(), 2)
        
        completed_todos = Todo.objects.completed()
        self.assertEqual(completed_todos.count(), 1)
        self.assertEqual(completed_todos.first(), completed_todo)
        
        pending_todos = Todo.objects.pending()
        self.assertEqual(pending_todos.count(), 1)
        self.assertEqual(pending_todos.first(), pending_todo)
    
    def test_todo_unique_title_per_user(self):
        self.create_todo(title='Unique Title')
        
        with self.assertRaises(Exception):
            self.create_todo(title='Unique Title')
        
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            phone_number='+996777987654',
            password='pass123'
        )
        
        from apps.todo.models import Todo
        Todo.objects.create(
            title='Unique Title',
            description='Different user todo',
            owner=other_user
        )
    
    def test_todo_title_min_length_validation(self):
        with self.assertRaises(Exception):
            todo = Todo(title='AB', owner=self.user)
            todo.save()
    
    def test_todo_ordering(self):
        todo1 = self.create_todo(title='Todo 1')
        todo2 = self.create_todo(title='Todo 2')
        todo3 = self.create_todo(title='Todo 3')
        
        todos = Todo.objects.all()
        
        self.assertEqual(todos[0], todo3)
        self.assertEqual(todos[1], todo2)
        self.assertEqual(todos[2], todo1)
    
    def test_todo_image_upload_path(self):
        todo = self.create_todo()
        
        self.assertEqual(todo.image.upload_to, 'todo_images/%Y/%m/')
    
    def test_todo_is_overdue_property(self):
        todo = self.create_todo()
        self.assertFalse(todo.is_overdue)
        
        todo.is_completed = True
        todo.save()
        self.assertFalse(todo.is_overdue)


class TodoModelWithImageTest(BaseTestCase):
    
    def test_todo_with_image(self):
        image_file = self.create_image_file()
        
        todo = self.create_todo()
        todo.image.save('test.jpg', image_file, save=True)
        
        self.assertIsNotNone(todo.image)
        self.assertTrue(todo.image.name.endswith('.jpg'))
    
    def test_todo_image_optional(self):
        todo = self.create_todo()
        self.assertFalse(bool(todo.image))
        
        todo.save()
        self.assertFalse(bool(todo.image))
