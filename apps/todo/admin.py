from django.contrib import admin
from .models import ToDo

@admin.register(ToDo)
class ToDoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'is_completed', 'created_at')
    list_editable = ('is_completed',)
    list_filter = ('is_completed', 'created_at', 'owner')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)