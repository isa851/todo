from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    
    list_display = [
        'username', 'email', 'phone_number', 'age', 
        'is_active', 'is_staff', 'created_at', 'todos_count'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 
        'created_at', 'age'
    ]
    search_fields = ['username', 'email', 'phone_number', 'first_name', 'last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'last_login', 'todos_count']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'age')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 
                'groups', 'user_permissions'
            )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at')
        }),
        (_('Statistics'), {
            'fields': ('todos_count',),
            'classes': ('collapse',)
        })
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'phone_number', 'age', 
                'password1', 'password2'
            ),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            todos_count=Count('todos', distinct=True)
        )
    
    def todos_count(self, obj):
        count = obj.todos.count()
        if count > 0:
            url = f'/admin/todo/todo/?owner__id__exact={obj.id}'
            return format_html(
                '<a href="{}">{} todos</a>', url, count
            )
        return '0 todos'
    todos_count.short_description = _('Todos')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['created_at']
        return self.readonly_fields
