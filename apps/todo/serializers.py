from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Todo
from core.exceptions import ValidationError, ConflictError, NotFoundError


class TodoCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Todo
        fields = ['title', 'description', 'image']
        extra_kwargs = {
            'title': {
                'help_text': _('Title of the todo item (minimum 3 characters)')
            },
            'description': {
                'help_text': _('Detailed description of the todo item')
            },
            'image': {
                'help_text': _('Optional image for the todo item')
            }
        }

    def validate_title(self, value):
        user = self.context['request'].user
        if Todo.objects.filter(owner=user, title__iexact=value).exists():
            raise ConflictError(_('You already have a todo with this title'))
        return value.strip()

    def validate_image(self, value):
        if value:
            max_size = 5 * 1024 * 1024
            if value.size > max_size:
                raise ValidationError(_('Image size must be less than 5MB'))
            
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            file_extension = value.name.lower().split('.')[-1]
            if file_extension not in allowed_extensions:
                raise ValidationError(
                    _('Image format not supported. Allowed formats: JPG, JPEG, PNG, GIF, WEBP')
                )
        return value

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class TodoUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Todo
        fields = ['title', 'description', 'is_completed', 'image']
        extra_kwargs = {
            'title': {
                'help_text': _('Title of the todo item (minimum 3 characters)')
            },
            'description': {
                'help_text': _('Detailed description of the todo item')
            },
            'is_completed': {
                'help_text': _('Whether the todo item is completed')
            },
            'image': {
                'help_text': _('Optional image for the todo item')
            }
        }

    def validate_title(self, value):
        user = self.context['request'].user
        if Todo.objects.filter(owner=user, title__iexact=value).exclude(pk=self.instance.pk).exists():
            raise ConflictError(_('You already have a todo with this title'))
        return value.strip()

    def validate_image(self, value):
        if value:
            max_size = 5 * 1024 * 1024
            if value.size > max_size:
                raise ValidationError(_('Image size must be less than 5MB'))
            
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            file_extension = value.name.lower().split('.')[-1]
            if file_extension not in allowed_extensions:
                raise ValidationError(
                    _('Image format not supported. Allowed formats: JPG, JPEG, PNG, GIF, WEBP')
                )
        return value


class TodoDetailSerializer(serializers.ModelSerializer):
    
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    status_display = serializers.ReadOnlyField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Todo
        fields = [
            'id', 'title', 'description', 'is_completed', 'status_display',
            'created_at', 'updated_at', 'completed_at', 'image', 'image_url',
            'owner_username', 'owner_email'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'owner_username', 'owner_email']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class TodoListSerializer(serializers.ModelSerializer):
    
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    status_display = serializers.ReadOnlyField()
    image_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Todo
        fields = [
            'id', 'title', 'is_completed', 'status_display',
            'created_at', 'owner_username', 'image_thumbnail'
        ]

    def get_image_thumbnail(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class TodoBulkActionSerializer(serializers.Serializer):
    
    todo_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text=_('List of todo IDs to perform action on')
    )
    action = serializers.ChoiceField(
        choices=['mark_complete', 'mark_incomplete', 'delete'],
        help_text=_('Action to perform on selected todos')
    )

    def validate_todo_ids(self, value):
        user = self.context['request'].user
        existing_todos = Todo.objects.filter(
            owner=user,
            id__in=value
        ).values_list('id', flat=True)
        
        missing_ids = set(str(id) for id in value) - set(str(id) for id in existing_todos)
        if missing_ids:
            raise NotFoundError(
                _('The following todos were not found: %(ids)s') % 
                {'ids': ', '.join(missing_ids)}
            )
        
        return value
