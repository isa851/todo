from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
import uuid


class TodoManager(models.Manager):
    
    def get_queryset(self):
        return super().get_queryset().select_related('owner')
    
    def completed(self):
        return self.get_queryset().filter(is_completed=True)
    
    def pending(self):
        return self.get_queryset().filter(is_completed=False)
    
    def for_user(self, user):
        return self.get_queryset().filter(owner=user)


class Todo(models.Model):
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_('Unique identifier for the todo item')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='todos',
        verbose_name=_('owner'),
        help_text=_('User who owns this todo item')
    )
    title = models.CharField(
        _('title'),
        max_length=255,
        validators=[MinLengthValidator(3)],
        help_text=_('Title of the todo item (minimum 3 characters)')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Detailed description of the todo item')
    )
    is_completed = models.BooleanField(
        _('is completed'),
        default=False,
        help_text=_('Whether the todo item is completed')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('Date and time when the todo item was created')
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('Date and time when the todo item was last updated')
    )
    completed_at = models.DateTimeField(
        _('completed at'),
        null=True,
        blank=True,
        help_text=_('Date and time when the todo item was completed')
    )
    image = models.ImageField(
        _('image'),
        upload_to='todo_images/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Optional image for the todo item')
    )
    
    objects = TodoManager()

    class Meta:
        db_table = 'todos'
        ordering = ['-created_at']
        verbose_name = _('Todo')
        verbose_name_plural = _('Todos')
        unique_together = ['owner', 'title']
        indexes = [
            models.Index(fields=['owner', 'created_at']),
            models.Index(fields=['is_completed']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.owner.username}"
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.is_completed and self.completed_at:
            self.completed_at = None
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        return False
    
    @property
    def status_display(self):
        return _('Completed') if self.is_completed else _('Pending')
