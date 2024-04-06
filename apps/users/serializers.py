from typing import TYPE_CHECKING, override

from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users import models

if TYPE_CHECKING:
    from collections.abc import Sequence


class AdminOnlyFieldsSerializerMixin:
    """Serializer mixin to remove fields if the user is not an admin.

    ```python

    # Usage:

    class MyActivityModelSerializer(
        AdminOnlyFieldsSerializerMixin,
        ActivitySerializer
    ):
        ...

    serializer = MyActivityModelSerializer(
        context={"request": request},
        admin_only=["user", "content_type"],
    )

    ```
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the serializer."""
        admin_only_fields = set(
            kwargs.pop(
                "admin_only",
                getattr(self.Meta, "admin_only", []),  # type: ignore[attr-defined]
            ),
        )
        super().__init__(*args, **kwargs)

        context = kwargs.get("context")
        if not context:
            return

        request = context.get("request")
        if not request:
            return

        if request.user and not getattr(request.user, "is_superuser", False):
            for field_name in admin_only_fields:
                self.fields.pop(field_name)  # type: ignore[attr-defined]


class UserSerializer(AdminOnlyFieldsSerializerMixin, serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    groups = serializers.SlugRelatedField(
        slug_field="name",
        many=True,
        queryset=Group.objects.all(),
        read_only=False,
        required=False,
    )

    class Meta:
        model = models.User
        fields = (
            "id",
            "email",
            "name",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "groups",
            "phone_number",
        )
        read_only_fields = (
            "id",
            "is_active",
            "is_staff",
            "is_superuser",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }
        admin_only = ("is_superuser", "is_staff", "is_active")

    def create(self, validated_data):
        groups: Sequence[Group] | None = validated_data.pop("groups")
        if not groups or len(groups) == 0:
            groups = models.User.get_default_groups()
        user = models.User.objects.create_user(**validated_data)
        user.groups.set(groups)
        return user


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    """User token obtain pair serializer."""

    @override
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["phone_number"] = str(user.phone_number)
        token["email"] = user.email
        token["name"] = user.name
        token["groups"] = list(user.groups.values_list("name", flat=True))

        return token
