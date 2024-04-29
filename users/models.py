from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


NULLABLE = {'null': True, 'blank': True}


class UserManager(BaseUserManager):
    """ Менеджер для модели User. """
    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError("The given username must be set")
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        phone = GlobalUserModel.normalize_username(phone)
        user = self.model(phone=phone, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(phone, password, **extra_fields)


class User(AbstractUser):
    """ Модель для сущности User (Пользователь)"""
    objects = UserManager()

    username = None
    email = models.EmailField(verbose_name='Email', **NULLABLE)
    avatar = models.ImageField(upload_to='users/', verbose_name='Аватар', **NULLABLE)
    phone = models.CharField(max_length=35, unique=True, verbose_name='Номер телефона')
    city = models.CharField(max_length=50, verbose_name='Город', **NULLABLE)
    telegram_id = models.CharField(max_length=100, verbose_name='Телеграм ID', **NULLABLE)
    auth_code = models.CharField(max_length=4, verbose_name='Код авторизации', **NULLABLE)
    invite_code = models.CharField(max_length=6, unique=True, verbose_name='Invite код', **NULLABLE)
    referral_code = models.CharField(max_length=6, verbose_name='Код реферала', **NULLABLE)
    referrals = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='Рефералы',
                                  **NULLABLE)

    is_active = models.BooleanField(default=False, verbose_name='Состояние активности')
    is_staff = models.BooleanField(default=False, verbose_name='Сотрудник')
    is_superuser = models.BooleanField(default=False, verbose_name='Администратор')
    is_authenticate = models.BooleanField(default=False, verbose_name='Признак авторизации')

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'ID: {self.id} / Phone: {self.phone} / Status: {self.is_active} / Auth: {self.is_authenticate}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
