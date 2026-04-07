from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True, verbose_name="Имя пользователя")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    phone_regex = RegexValidator(
        regex=r'^\+996\d{9}$',
        message="Номер телефона должен быть в формате: '+996XXXXXXXXX'.",
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=13,
        unique=True,
        verbose_name="Номер телефона",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    age = models.PositiveIntegerField(verbose_name="Возраст")

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email', 'age']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"