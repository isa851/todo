from django.db import models
from core import settings

# Create your models here.

class ToDo(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='todos',
        verbose_name="Владелец"
    )
    title = models.CharField(max_length=150, unique=True, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    is_completed = models.BooleanField(default=False, verbose_name="Выполнено:")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    image = models.ImageField(
        upload_to='todo_images/',
        verbose_name="Изображение",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self):
        return self.title