import uuid
from enum import Enum
from typing import ClassVar, override

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as AuthGroup
from django.db.models import CharField, EmailField, UUIDField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .managers import UserManager


class Group(Enum):
    """Enum for user groups.

    This enum is used to define the user groups in the application.
    """

    OPERATORS = "operators"
    USERS = "users"


class User(AbstractUser):
    """
    Default custom user model for Back-end of the advisor.ai project.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    id = UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = CharField(_("Name of the user"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("Email address"), unique=True)
    username = None  # type: ignore[assignment]
    phone_number = PhoneNumberField(_("Phone number"), blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    @override
    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        self.groups.add(*self.get_default_groups())

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns
        -------
            str: URL for user detail.

        """
        return reverse("user-detail", kwargs={"pk": self.pk})

    @staticmethod
    def get_default_groups():
        """Get the default user groups.

        Returns
        -------
            Iterable[Group]: Iterable of groups.

        """
        return AuthGroup.objects.filter(name__in=[Group.USERS.value])
