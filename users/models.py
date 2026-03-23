from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models

def user_avatar_path(instance, filename):
# Файл будет загружен в media/avatars/user_<id>/<filename>
    return f'avatars/user_{instance.user.id}/{filename}'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        if not username:
            raise ValueError("Username обязателен")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, db_index=True, verbose_name='email')
    username = models.CharField(unique=True, max_length=128, db_index=True, verbose_name='ник')
    phone_number = models.CharField(max_length=64, db_index=True, verbose_name='номер телефона', blank=True)

    is_active = models.BooleanField(default=True, verbose_name='активен')
    is_staff = models.BooleanField(default=False, verbose_name='сотрудник')
    is_deleted = models.BooleanField(default=False, verbose_name='удалён')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='дата изменения')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'аккаунт'
        verbose_name_plural = 'аккаунты'

    def __str__(self):
        return self.email



class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'мужской'),
        ('female', 'женский')
    ]

    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='пользователь'
    )
    first_name = models.CharField(max_length=128, verbose_name='имя', blank=True)
    last_name = models.CharField(max_length=128, verbose_name='фамилия', blank=True)
    bio = models.TextField(blank=True, null=True, verbose_name='био')
    points = models.IntegerField(default=0, verbose_name='баллы')
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True,
        blank=True,
        verbose_name='аватар'
    )
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='дата рождения')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, verbose_name='пол')
    city = models.CharField(max_length=128, blank=True, verbose_name='город')
    specialty = models.CharField(max_length=255, blank=True, verbose_name='специальность')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='обновлено')

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self):
        return f"Профиль: {self.user.username}"
