# Todo App API Documentation

## Overview

A comprehensive Django REST API for managing user tasks with JWT authentication, built with professional development practices.

## Features

- **JWT Authentication** with refresh tokens
- **User Management** with phone validation (+996)
- **Todo CRUD Operations** with image support
- **Advanced Filtering & Search**
- **Bulk Operations** on todos
- **Statistics & Analytics**
- **Comprehensive Error Handling**
- **Logging & Monitoring**
- **Admin Interface**
- **Test Coverage**

## Base URL

```
http://localhost:8000/api/
```

## Authentication

All endpoints (except registration and login) require JWT authentication.

### Login
```http
POST /api/users/login/
Content-Type: application/json

{
    "username": "testuser",
    "password": "yourpassword"
}
```

**Response:**
```json
{
    "message": "Login successful",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "testuser",
        "email": "test@example.com",
        "phone_number": "+996555123456",
        "age": 25,
        "todos_count": 0,
        "completed_todos_count": 0
    }
}
```

### Registration
```http
POST /api/users/register/
Content-Type: application/json

{
    "username": "newuser",
    "email": "newuser@example.com",
    "phone_number": "+996555123456",
    "age": 25,
    "password": "password123",
    "confirm_password": "password123"
}
```

## User Endpoints

### Get Current User Profile
```http
GET /api/users/me/
Authorization: Bearer <access_token>
```

### Update Current User Profile
```http
PATCH /api/users/me/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "age": 26,
    "first_name": "John",
    "last_name": "Doe"
}
```

### Change Password
```http
POST /api/users/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "old_password": "oldpassword",
    "new_password": "newpassword123",
    "confirm_password": "newpassword123"
}
```

### Delete Account
```http
DELETE /api/users/delete-account/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "password": "yourpassword"
}
```

## Todo Endpoints

### List Todos
```http
GET /api/todos/
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `is_completed` - Filter by completion status
- `created_after` - Filter todos created after date
- `created_before` - Filter todos created before date
- `search` - Search in title and description
- `ordering` - Order by field (created_at, -created_at, title, is_completed)
- `page` - Page number
- `page_size` - Items per page (max 100)

**Response:**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/todos/?page=2",
    "previous": null,
    "total_pages": 2,
    "current_page": 1,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Complete project",
            "is_completed": false,
            "status_display": "Pending",
            "created_at": "2024-01-15T10:30:00Z",
            "owner_username": "testuser",
            "image_thumbnail": "http://localhost:8000/media/todo_images/2024/01/image.jpg"
        }
    ],
    "statistics": {
        "total": 25,
        "completed": 10,
        "pending": 15,
        "completion_rate": 40.0
    }
}
```

### Create Todo
```http
POST /api/todos/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

title: "New Task"
description: "Task description"
image: <file>
```

### Get Todo Details
```http
GET /api/todos/<uuid:pk>/
Authorization: Bearer <access_token>
```

### Update Todo
```http
PATCH /api/todos/<uuid:pk>/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "Updated Task",
    "is_completed": true
}
```

### Delete Todo
```http
DELETE /api/todos/<uuid:pk>/
Authorization: Bearer <access_token>
```

### Delete All Todos
```http
DELETE /api/todos/delete-all/
Authorization: Bearer <access_token>
```

### Bulk Actions
```http
POST /api/todos/bulk-actions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "todo_ids": [
        "550e8400-e29b-41d4-a716-446655440000",
        "550e8400-e29b-41d4-a716-446655440001"
    ],
    "action": "mark_complete"
}
```

**Actions:** `mark_complete`, `mark_incomplete`, `delete`

### Get Statistics
```http
GET /api/todos/statistics/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "statistics": {
        "total": 25,
        "completed": 10,
        "pending": 15,
        "completion_rate": 40.0,
        "recent_todos": 5
    }
}
```

## Error Responses

All errors return consistent format:

```json
{
    "detail": "Error message",
    "code": "error_code"
}
```

### Common Error Codes

- `authentication_failed` - Invalid credentials
- `permission_denied` - Access denied
- `not_found` - Resource not found
- `validation_error` - Invalid input data
- `conflict` - Resource already exists
- `rate_limit_exceeded` - Too many requests

## Phone Number Validation

Phone numbers must be in format: `+996XXXXXXXXX`

Valid examples:
- `+996555123456`
- `+996777987654`
- `+996222111333`

## Image Upload

- **Formats:** JPG, JPEG, PNG, GIF, WEBP
- **Max Size:** 5MB
- **Upload Path:** `/media/todo_images/YYYY/MM/`

## Rate Limiting

- Login: 5 attempts per minute
- Registration: 3 attempts per minute
- General API: 1000 requests per hour

## Pagination

Default page size: 20 items
Maximum page size: 100 items

## Search

Search is performed on:
- Todo title
- Todo description

Search is case-insensitive and supports partial matches.

## Filtering

Available filters for todos:
- `is_completed` - Boolean filter
- `created_after` - Date filter (ISO format)
- `created_before` - Date filter (ISO format)
- `completed_after` - Date filter (ISO format)
- `completed_before` - Date filter (ISO format)

## Ordering

Available ordering fields:
- `created_at` - Creation time
- `-created_at` - Creation time (descending)
- `updated_at` - Update time
- `-updated_at` - Update time (descending)
- `title` - Alphabetical
- `is_completed` - Completion status

## Development

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users
python manage.py test apps.todo

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Admin Interface

Access admin panel at: `http://localhost:8000/admin/`

Features:
- User management with todo statistics
- Todo management with status badges
- Advanced filtering and search
- Custom admin interface

## Security Features

- JWT authentication with refresh tokens
- Phone number validation
- Password strength requirements
- Rate limiting
- CORS protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## Logging

Logs are stored in `/logs/` directory:
- `todo_app.log` - General application logs
- `todo_app_errors.log` - Error logs only

Log rotation: 10MB max file size, 5 backup files

## Performance

- Database query optimization with select_related/prefetch_related
- Database indexes on frequently queried fields
- Pagination for large datasets
- Image compression and optimization
- Caching support (Redis/Memcached ready)

## API Versioning

Current version: v1

Future versions will be accessible via:
- `/api/v2/...`

## Support

For issues and questions:
1. Check the documentation
2. Review error messages
3. Check logs for detailed information
4. Contact development team
