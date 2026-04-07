import re
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models


class PhoneNumberValidator:
    
    @staticmethod
    def validate(value):
        pattern = r'^\+996\d{9}$'
        if not re.match(pattern, value):
            raise ValidationError(
                _('Phone number must be in format +996XXXXXXXXX (e.g., +996555123456)'),
                code='invalid_phone_format'
            )


class UserManager(models.Manager):
    
    def get_by_natural_key(self, username):
        return self.get(username__iexact=username)
    
    def create_user(self, username, email, phone_number, password=None, **extra_fields):
        if not username:
            raise ValueError(_('The Username must be set'))
        if not email:
            raise ValueError(_('The Email must be set'))
        if not phone_number:
            raise ValueError(_('The Phone number must be set'))
        
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. 254 characters or fewer. Must be a valid email address.')
    )
    phone_number = models.CharField(
        _('phone number'),
        max_length=13,
        unique=True,
        validators=[PhoneNumberValidator.validate],
        help_text=_('Phone number in format +996XXXXXXXXX')
    )
    age = models.PositiveIntegerField(
        _('age'),
        null=True,
        blank=True,
        help_text=_('User age in years')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('Date and time when user account was created')
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number']

    class Meta:
        db_table = 'auth_user'
        ordering = ['-created_at']
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
        ]

    def __str__(self):
        return f"@{self.username}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
