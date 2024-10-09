from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from dotenv import load_dotenv

load_dotenv()


class CustomManager(BaseUserManager):
    """Кастомный менеджер для управления пользователями."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Поле email обязательно к заполнению.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователей."""

    username_validator = UnicodeUsernameValidator()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    ADMIN_ROLE = 'admin'
    USER_ROLE = 'user'

    AVAILABLE_ROLES = [
        ('admin', 'administrator'),
        ('user', 'user')
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Никнейм',
        validators=[username_validator],
    )
    password = models.CharField(
        max_length=128,
        verbose_name='Пароль'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронный адрес',
    )
    avatar = models.ImageField(
        upload_to='users/avatar/',
        null=True,
        default=None,
    )
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'пользователя'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    objects = CustomManager()

    def has_perm(self, perm, obj=None):
        return self.is_staff and self.is_active

    def has_module_perms(self, app_label):
        return self.is_staff and self.is_active

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff is True


class Subscription(models.Model):
    """Модель подписок."""

    subscriptions = models.ForeignKey(
        CustomUser,
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    subscribers = models.ForeignKey(
        CustomUser,
        related_name='subscribers',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscriptions', 'subscribers'],
                name='unique_subs'
            )
        ]

    def save(self, *args, **kwargs):
        if self.subscriptions == self.subscribers:
            raise ValueError("Нельзя подписываться на себя.")
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f'пользователь {self.subscribers.username} подписан на '
            f'пользователя {self.subscriptions.username}'
        )
