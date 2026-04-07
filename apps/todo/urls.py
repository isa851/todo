from django.urls import path
from .views import (
    TodoListView,
    TodoDetailView,
    delete_all_todos,
    bulk_todo_actions,
    todo_statistics
)


urlpatterns = [
    path('', TodoListView.as_view(), name='todo-list'),
    path('<uuid:pk>/', TodoDetailView.as_view(), name='todo-detail'),
    path('delete-all/', delete_all_todos, name='delete-all-todos'),
    path('bulk-actions/', bulk_todo_actions, name='bulk-todo-actions'),
    path('statistics/', todo_statistics, name='todo-statistics'),
]
