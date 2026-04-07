import django_filters
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import Todo
from .serializers import (
    TodoCreateSerializer,
    TodoUpdateSerializer,
    TodoDetailSerializer,
    TodoListSerializer,
    TodoBulkActionSerializer
)
from core.permissions import IsOwner
from core.exceptions import ValidationError, NotFoundError
from apps.users.views import StandardResultsSetPagination


class TodoFilter(django_filters.FilterSet):
    
    is_completed = django_filters.BooleanFilter(field_name='is_completed')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    completed_after = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='gte')
    completed_before = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='lte')
    
    class Meta:
        model = Todo
        fields = ['is_completed']


class TodoListView(generics.ListCreateAPIView):
    
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TodoFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title', 'is_completed']
    ordering = ['-created_at']

    def get_queryset(self):
        return Todo.objects.for_user(self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TodoCreateSerializer
        return TodoListSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            todo = serializer.save()
            
            return Response({
                'message': _('Todo created successfully'),
                'todo': TodoDetailSerializer(todo, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            raise ValidationError(str(e))

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            
            total_todos = queryset.count()
            completed_todos = queryset.filter(is_completed=True).count()
            pending_todos = total_todos - completed_todos
            
            return self.get_paginated_response({
                'results': serializer.data,
                'statistics': {
                    'total': total_todos,
                    'completed': completed_todos,
                    'pending': pending_todos,
                    'completion_rate': round((completed_todos / total_todos * 100) if total_todos > 0 else 0, 2)
                }
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'pk'

    def get_queryset(self):
        return Todo.objects.for_user(self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TodoUpdateSerializer
        return TodoDetailSerializer

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            todo = serializer.save()
            
            return Response({
                'message': _('Todo updated successfully'),
                'todo': TodoDetailSerializer(todo, context={'request': request}).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            raise ValidationError(str(e))

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            
            return Response({
                'message': _('Todo deleted successfully')
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            raise ValidationError(str(e))


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_all_todos(request):
    
    try:
        deleted_count, _ = Todo.objects.filter(owner=request.user).delete()
        
        return Response({
            'message': _('Successfully deleted %(count)d todos') % {'count': deleted_count},
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        raise ValidationError(str(e))


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_todo_actions(request):
    
    try:
        serializer = TodoBulkActionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        todo_ids = serializer.validated_data['todo_ids']
        action = serializer.validated_data['action']
        
        todos = Todo.objects.filter(id__in=todo_ids, owner=request.user)
        
        if action == 'mark_complete':
            updated_count = todos.update(is_completed=True)
            message = _('Marked %(count)d todos as completed') % {'count': updated_count}
        elif action == 'mark_incomplete':
            updated_count = todos.update(is_completed=False)
            message = _('Marked %(count)d todos as incomplete') % {'count': updated_count}
        elif action == 'delete':
            deleted_count, _ = todos.delete()
            message = _('Deleted %(count)d todos') % {'count': deleted_count}
        else:
            raise ValidationError(_('Invalid action'))
        
        return Response({
            'message': message,
            'affected_count': todos.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        raise ValidationError(str(e))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def todo_statistics(request):
    
    try:
        todos = Todo.objects.filter(owner=request.user)
        
        total_todos = todos.count()
        completed_todos = todos.filter(is_completed=True).count()
        pending_todos = total_todos - completed_todos
        
        from django.utils import timezone
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        recent_todos = todos.filter(created_at__gte=week_ago).count()
        
        completion_rate = round((completed_todos / total_todos * 100) if total_todos > 0 else 0, 2)
        
        return Response({
            'statistics': {
                'total': total_todos,
                'completed': completed_todos,
                'pending': pending_todos,
                'completion_rate': completion_rate,
                'recent_todos': recent_todos
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        raise ValidationError(str(e))
