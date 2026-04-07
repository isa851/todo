from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserListView,
    UserDetailView,
    CurrentUserView,
    change_password,
    delete_account
)


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('', UserListView.as_view(), name='user-list'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('change-password/', change_password, name='change-password'),
    path('delete-account/', delete_account, name='delete-account'),
    path('<uuid:pk>/', UserDetailView.as_view(), name='user-detail'),
]
