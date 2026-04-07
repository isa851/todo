from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserListSerializer
)
from core.exceptions import ValidationError, NotFoundError


class StandardResultsSetPagination(PageNumberPagination):
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class UserRegistrationView(generics.CreateAPIView):
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            return Response({
                'message': _('User registered successfully'),
                'user': UserProfileSerializer(user, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            raise ValidationError(str(e))


class UserLoginView(generics.GenericAPIView):
    
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = serializer.validated_data['user']
            
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': _('Login successful'),
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserProfileSerializer(user, context={'request': request}).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            raise ValidationError(str(e))


class UserListView(generics.ListAPIView):
    
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return User.objects.annotate(
            todos_count=Count('todos'),
            completed_todos_count=Count('todos', filter=Q(todos__is_completed=True))
        )


class UserDetailView(generics.RetrieveAPIView):
    
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    pagination_class = None

    def get_queryset(self):
        return User.objects.annotate(
            todos_count=Count('todos'),
            completed_todos_count=Count('todos', filter=Q(todos__is_completed=True))
        )


class CurrentUserView(generics.RetrieveUpdateAPIView):
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({
                'message': _('Profile updated successfully'),
                'user': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            raise ValidationError(str(e))


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not old_password or not new_password or not confirm_password:
        raise ValidationError(_('All password fields are required'))
    
    if new_password != confirm_password:
        raise ValidationError(_('New passwords do not match'))
    
    if len(new_password) < 8:
        raise ValidationError(_('Password must be at least 8 characters long'))
    
    user = request.user
    if not user.check_password(old_password):
        raise ValidationError(_('Current password is incorrect'))
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'message': _('Password changed successfully')
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_account(request):
    
    password = request.data.get('password')
    if not password:
        raise ValidationError(_('Password is required to delete account'))
    
    user = request.user
    if not user.check_password(password):
        raise ValidationError(_('Password is incorrect'))
    
    user.delete()
    
    return Response({
        'message': _('Account deleted successfully')
    }, status=status.HTTP_200_OK)
