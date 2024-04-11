from typing import TYPE_CHECKING

from django.db.models.query import QuerySet
from rest_access_policy import AccessPolicy
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

if TYPE_CHECKING:
    from apps.suggestions.models import Suggestion


class SuggestionAccessPolicy(AccessPolicy):
    """Suggestion access policy."""

    statements = [
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": "admin",
            "effect": "allow",
        },
        {
            "action": ["retrieve"],
            "principal": "authenticated",
            "effect": "allow",
            "condition": "is_owner_or_staff",
        },
        {
            "action": ["list"],
            "principal": "authenticated",
            "effect": "allow",
        },
    ]

    def is_owner_or_staff(
        self, request: Request, view: GenericViewSet, *args, **kwargs
    ) -> bool:
        suggestion: Suggestion = view.get_object()
        return request.user == suggestion.user or request.user.is_staff

    @classmethod
    def scope_queryset(cls, request: Request, qs: QuerySet):
        """Scope the queryset so that common users can see only their suggestions."""
        return qs.filter(user=request.user) if not request.user.is_staff else qs

    @classmethod
    def scope_fields(cls, request: Request, fields: dict, *args, **kwargs) -> dict:
        """Hide the implementation detail fields for common users."""
        if not request.user.is_staff:
            fields.pop("value", None)
            fields.pop("review", None)
        return fields
