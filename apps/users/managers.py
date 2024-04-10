from typing import TYPE_CHECKING

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db.models import Q, QuerySet
from django.utils import timezone

if TYPE_CHECKING:
    from .models import User  # noqa: F401


class UserManager(DjangoUserManager["User"]):
    """Custom manager for the User model."""

    def _create_user(self, email: str, password: str | None, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            msg = "The given email must be set"
            raise ValueError(msg)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):  # type: ignore[override]
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):  # type: ignore[override]
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)
        if extra_fields.get("is_superuser") is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)

        return self._create_user(email, password, **extra_fields)

    def recent(self, days: int = 7, ids_only=None) -> list[int] | QuerySet:
        """Return the users that interacted with the application recently.

        Args:
            days (int, optional): The days to consider. Defaults to 7.
            ids_only (bool, optional): Return only the users IDs. Defaults to None.

        Returns:
            QuerySet | list[int]: The users queryset.
        """
        base_date = timezone.now() - timezone.timedelta(days=days)
        queryset = self.filter(
            Q(date_joined__gte=base_date) | Q(last_login__gte=base_date)
        ).values_list("id", flat=True)
        if ids_only:
            queryset = queryset.values_list("id", flat=True)
        return queryset
