from typing import TYPE_CHECKING

import pytest
from django.urls import resolve, reverse

from apps.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from apps.users.models import User


@pytest.mark.django_db()
def test_user_detail():
    user: User = UserFactory()
    assert reverse("user-detail", kwargs={"pk": user.pk}) == f"/users/{user.pk}/"
    assert resolve(f"/users/{user.pk}/").view_name == "user-detail"


def test_user_list():
    assert reverse("user-list") == "/users/"
    assert resolve("/users/").view_name == "user-list"


def test_user_me():
    assert reverse("user-me") == "/users/me/"
    assert resolve("/users/me/").view_name == "user-me"
