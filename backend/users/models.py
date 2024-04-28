from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


def name_validator(value):
    if value == "me":
        raise ValidationError('Имя "me" недопустимо.')


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        ADMIN = 'admin', 'Admin'
        MODERATOR = 'moderator', 'Moderator'

    username = models.CharField(
        'Юзернейм',
        max_length=150,
        unique=True,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z'),
                    name_validator],
    )
    email = models.EmailField(
        'Емэил',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        'Имя', max_length=150
    )
    last_name = models.CharField(
        'Фамилия', max_length=150
    )
    bio = models.TextField(
        'Био', blank=True, null=True
    )
    role = models.CharField(
        'Роль', choices=Role.choices, default=Role.USER, max_length=10
    )

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
