from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User
from core.exceptions import ValidationError, ConflictError


class UserRegistrationSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text=_('Password must be at least 8 characters long')
    )
    confirm_password = serializers.CharField(
        write_only=True,
        help_text=_('Confirm password')
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'age', 'password', 'confirm_password']
        extra_kwargs = {
            'username': {'help_text': _('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')},
            'email': {'help_text': _('Required. Valid email address.')},
            'phone_number': {'help_text': _('Phone number in format +996XXXXXXXXX')},
        }

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise ConflictError(_('Username already exists'))
        return value.lower()

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise ConflictError(_('Email already exists'))
        return value.lower()

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise ConflictError(_('Phone number already exists'))
        return value

    def validate_age(self, value):
        if value is not None and (value < 1 or value > 120):
            raise ValidationError(_('Age must be between 1 and 120'))
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        if password != confirm_password:
            raise ValidationError(_('Passwords do not match'))
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    
    username = serializers.CharField(help_text=_('Username or email'))
    password = serializers.CharField(
        write_only=True,
        help_text=_('Your password')
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise ValidationError(_('Invalid credentials'))
            
            if not user.is_active:
                raise ValidationError(_('User account is disabled'))
            
            attrs['user'] = user
            return attrs
        
        raise ValidationError(_('Must include username and password'))


class UserProfileSerializer(serializers.ModelSerializer):
    
    full_name = serializers.ReadOnlyField()
    todos_count = serializers.SerializerMethodField()
    completed_todos_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_number', 'age',
            'first_name', 'last_name', 'full_name', 'created_at',
            'todos_count', 'completed_todos_count'
        ]
        read_only_fields = ['id', 'username', 'created_at']

    def get_todos_count(self, obj):
        return obj.todos.count()

    def get_completed_todos_count(self, obj):
        return obj.todos.filter(is_completed=True).count()

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exclude(pk=self.instance.pk).exists():
            raise ConflictError(_('Phone number already exists'))
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exclude(pk=self.instance.pk).exists():
            raise ConflictError(_('Email already exists'))
        return value.lower()

    def validate_age(self, value):
        if value is not None and (value < 1 or value > 120):
            raise ValidationError(_('Age must be between 1 and 120'))
        return value


class UserListSerializer(serializers.ModelSerializer):
    
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'age', 'full_name', 'created_at']
        read_only_fields = ['id', 'created_at']
