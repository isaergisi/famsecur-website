from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("E-posta adresi zorunludur.")
        user = self.model(email=self.normalize_email(email).lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.update(is_staff=True, is_superuser=True, role=User.Role.ADMIN)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """E-posta ile giriş yapan kullanıcı. Ebeveyn veya yönetici rolündedir."""

    class Role(models.TextChoices):
        PARENT = "parent", "Ebeveyn"
        ADMIN = "admin", "Yönetici"

    username = None
    email = models.EmailField("e-posta", unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PARENT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    def __str__(self) -> str:
        return self.email
