from typing import Any

import pytest
from django.db import models
from django.test import Client
from pytest_assert_utils import assert_model_attrs
from pytest_common_subject import precondition_fixture
from pytest_drf import (
    AsAnonymousUser,
    AsUser,
    Returns200,
    Returns201,
    Returns204,
    Returns401,
    Returns403,
    UsesDeleteMethod,
    UsesDetailEndpoint,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPatchMethod,
    UsesPostMethod,
    ViewSetTest,
)
from pytest_drf.util import pluralized, url_for
from pytest_lambda.fixtures import lambda_fixture, static_fixture

from apps.users.models import User
from apps.users.tests.factories import UserFactory


class JsonArrayAgg(models.aggregates.Aggregate):
    """Custom aggregation expression to group and process related objects."""

    function = "JSON_GROUP_ARRAY"
    output_field = models.JSONField()
    template = "%(function)s(%(distinct)s%(expressions)s)"
    allow_distinct = True


def express_user_for_admin(user: User) -> dict[str, Any]:
    """Express a user as a dictionary."""
    return {
        "id": str(user.pk),
        "email": user.email,
        "phone_number": str(user.phone_number),
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "name": user.name,
        "groups": list(user.groups.values_list("name", flat=True)),
        "date_joined": str(user.date_joined.strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
    }


def express_user_for_client(user: User) -> dict[str, Any]:
    """Express a user as a dictionary."""
    return {
        "id": str(user.pk),
        "email": user.email,
        "phone_number": str(user.phone_number),
        "name": user.name,
        "groups": list(user.groups.values_list("name", flat=True)),
        "date_joined": str(user.date_joined.strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
    }


express_users_list = pluralized(express_user_for_admin)


class DescribeUserViewSet(ViewSetTest):
    list_url = lambda_fixture(lambda: url_for("user-list"))
    detail_url = lambda_fixture(lambda user: url_for("user-detail", user.pk))

    class CaseAdmin(AsUser("admin")):  # type: ignore[misc]
        class DescribeList(
            UsesGetMethod,
            UsesListEndpoint,
            Returns200,
        ):
            users = lambda_fixture(
                lambda db: [UserFactory.create() for _ in range(3)],
            )

            def it_returns_all_users(
                self,
                users: list[User],
                results: list[dict[str, Any]],
            ):
                expected = express_users_list(users)
                actual = results
                for user in expected:
                    assert user in actual

        class DescribeCreate(
            UsesPostMethod,
            UsesListEndpoint,
            Returns201,
        ):
            data = static_fixture(
                {
                    "email": "william.fernandes@bix.com",
                    "password": "123456",
                    "name": "William Fernandes",
                    "phone_number": "+5511964858088",
                    "groups": ["operators"],
                },
            )

            initial_user_ids = precondition_fixture(
                lambda db: {
                    str(uuid) for uuid in User.objects.values_list("id", flat=True)
                },
                async_=False,
            )

            def it_creates_a_new_user(
                self,
                initial_user_ids: set[str],
                json: dict[str, Any],
            ):
                expected = initial_user_ids | {json["id"]}
                actual = {
                    str(uuid)
                    for uuid in User.objects.exclude(is_superuser=True).values_list(
                        "id",
                        flat=True,
                    )
                }
                assert actual == expected

            def it_sets_expected_attrs(
                self,
                data: dict[str, Any],
                json: dict[str, Any],
            ):
                user = User.objects.annotate(
                    group_names=JsonArrayAgg("groups__name", distinct=True),
                ).get(email=json["email"])
                data.pop("password")
                data["group_names"] = data.pop("groups")
                expected = data
                assert_model_attrs(user, expected)

        class DescribeRetrieve(
            UsesGetMethod,
            UsesDetailEndpoint,
            Returns200,
        ):
            def it_returns_the_user(self, user: User, json: dict[str, Any]):
                expected = express_user_for_admin(user)
                actual = json
                assert actual == expected

        class DescribeUpdate(
            UsesPatchMethod,
            UsesDetailEndpoint,
            Returns200,
        ):
            data = lambda_fixture(lambda faker: {"name": faker.name()})

            def it_sets_expected_attrs(self, data: dict[str, Any], user: User):
                user.refresh_from_db()
                expected = data
                assert_model_attrs(user, expected)

            def it_returns_key_value(self, user: User, json: dict[str, Any]):
                user.refresh_from_db()
                expected = express_user_for_admin(user)
                actual = json
                assert expected == actual

        class DescribeDestroy(
            UsesDeleteMethod,
            UsesDetailEndpoint,
            Returns204,
        ):
            initial_user_ids = precondition_fixture(
                lambda db: {
                    str(uuid) for uuid in User.objects.values_list("id", flat=True)
                },
                async_=False,
            )

            def it_deletes_user(self, user: User, initial_user_ids: set[str]):
                expected = initial_user_ids - {str(user.pk)}
                actual = set(User.objects.values_list("id", flat=True))
                assert expected == actual

    class CaseAuthenticated(AsUser("user")):  # type: ignore[misc]
        class DescribeList(
            UsesGetMethod,
            UsesListEndpoint,
            Returns403,
        ):
            """Users list is not allowed for authenticated users."""

        class DescribeRetrieve(
            UsesGetMethod,
            UsesDetailEndpoint,
            Returns200,
        ):
            def it_returns_the_user(self, user: User, json: dict[str, Any]):
                expected = express_user_for_client(user)
                actual = json
                assert actual == expected

        class DescribeUpdate(
            UsesPatchMethod,
            UsesDetailEndpoint,
            Returns200,
        ):
            data = lambda_fixture(lambda faker: {"name": faker.name()})

            def it_sets_expected_attrs(self, data: dict[str, Any], user: User):
                user.refresh_from_db()
                expected = data
                assert_model_attrs(user, expected)

            def it_returns_key_value(self, user: User, json: dict[str, Any]):
                user.refresh_from_db()
                expected = express_user_for_client(user)
                actual = json
                assert expected == actual

        class DescribeDestroy(
            UsesDeleteMethod,
            UsesDetailEndpoint,
            Returns204,
        ):
            initial_user_ids = precondition_fixture(
                lambda db: {
                    str(uuid) for uuid in User.objects.values_list("id", flat=True)
                },
                async_=False,
            )

            def it_deletes_user(self, user: User, initial_user_ids: set[str]):
                expected = initial_user_ids - {str(user.pk)}
                actual = set(User.objects.values_list("id", flat=True))
                assert expected == actual

    class CaseAnonymous(AsAnonymousUser):
        class DescribeCreate(
            UsesPostMethod,
            UsesListEndpoint,
            Returns201,
        ):
            data = static_fixture(
                {
                    "email": "william.fernandes@bix.com",
                    "password": "123456",
                    "name": "William Fernandes",
                    "phone_number": "+5527999073484",
                    "groups": ["operators"],
                },
            )

            initial_user_ids = precondition_fixture(
                lambda db: {
                    str(uuid) for uuid in User.objects.values_list("id", flat=True)
                },
                async_=False,
            )

            def it_creates_a_new_user(
                self,
                initial_user_ids: set[str],
                json: dict[str, Any],
            ):
                expected = initial_user_ids | {json["id"]}
                actual = {
                    str(uuid)
                    for uuid in User.objects.exclude(is_superuser=True).values_list(
                        "id",
                        flat=True,
                    )
                }
                assert actual == expected

            def it_sets_expected_attrs(
                self,
                data: dict[str, Any],
                json: dict[str, Any],
            ):
                user = User.objects.annotate(
                    group_names=JsonArrayAgg("groups__name", distinct=True),
                ).get(email=json["email"])
                data.pop("password")
                data["group_names"] = data.pop("groups")
                expected = data
                assert_model_attrs(user, expected)

        class DescribeRetrieve(
            UsesGetMethod,
            UsesDetailEndpoint,
            Returns401,
        ): ...

        class DescribeUpdate(
            UsesPatchMethod,
            UsesDetailEndpoint,
            Returns401,
        ): ...

        class DescribeDestroy(
            UsesDeleteMethod,
            UsesDetailEndpoint,
            Returns401,
        ): ...

    class CaseOtherUser:
        """Describe the behavior of a user interacting with another user's data."""

        @pytest.fixture()
        def client(self, client: Client, faker, db):
            client.force_login(UserFactory.create(email=faker.email()))
            return client

        class DescribeRetrieve(UsesGetMethod, UsesDetailEndpoint, Returns403): ...

        class DescribeUpdate(UsesPatchMethod, UsesDetailEndpoint, Returns403): ...

        class DescribeDestroy(UsesDeleteMethod, UsesDetailEndpoint, Returns403): ...
