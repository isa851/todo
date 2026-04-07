from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count
from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    
    list_display = [
        'title', 'owner', 'status_badge', 'created_at', 
        'updated_at', 'has_image'
    ]
    list_filter = [
        'is_completed', 'created_at', 'updated_at', 'owner'
    ]
    search_fields = ['title', 'description', 'owner__username', 'owner__email']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'owner')
        }),
        (_('Status'), {
            'fields': ('is_completed',)
        }),
        (_('Media'), {
            'fields': ('image',)
        }),
        (_('Timestamps'), {
            'fields': ('id', 'created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')
    
    def status_badge(self, obj):
        if obj.is_completed:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 8px; border-radius: 12px; font-size: 11px; '
                'font-weight: bold;">{}</span>',
                _('Completed')
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: black; '
                'padding: 3px 8px; border-radius: 12px; font-size: 11px; '
                'font-weight: bold;">{}</span>',
                _('Pending')
            )
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'is_completed'
    
    def has_image(self, obj):
        if obj.image:
            return format_html(
                '<span style="color: green;">✓</span>'
            )
        return format_html(
            '<span style="color: red;">✗</span>'
        )
    has_image.short_description = _('Image')
    has_image.admin_order_field = 'image'
    
    def get_list_filter(self, request):
        filters = super().get_list_filter(request)
        return filters
    
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        return queryset, use_distinct
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        super().delete_model(request, obj)


admin.site.site_header = _('Todo App Administration')
admin.site.site_title = _('Todo App Admin')
admin.site.index_title = _('Welcome to Todo App Administration')
