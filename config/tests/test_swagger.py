from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from apps.users.tests.factories import UserFactory


def test_swagger_accessible_by_admin(admin_client: Client):
    url = reverse("docs")
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_swagger_ui_not_accessible_by_normal_user(client: Client):
    url = reverse("docs")
    user = UserFactory()
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_api_schema_generated_successfully(admin_client: Client):
    url = reverse("schema")
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK
