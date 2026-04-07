from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Create your models here.

@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('id', 'phone_number', 'username', 'age', 'is_staff')
    list_display_links = ('id', 'phone_number', 'username')
    search_fields = ('phone_number', 'username')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('phone_number', 'age')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('phone_number', 'age')}),
    )