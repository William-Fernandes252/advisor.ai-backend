from typing import TYPE_CHECKING

from rest_access_policy import AccessPolicy
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

if TYPE_CHECKING:
    from apps.reviews.models import Review


class ReviewAccessPolicy(AccessPolicy):
    """Review access policy."""

    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": ["create"],
            "principal": "authenticated",
            "effect": "allow",
        },
        {
            "action": ["update", "partial_update", "destroy"],
            "principal": "authenticated",
            "effect": "allow",
            "condition": "is_author",
        },
    ]

    def is_author(
        self, request: Request, view: GenericViewSet, *args, **kwargs
    ) -> bool:
        """Return True if the user is the author of the review."""
        review: Review = view.get_object()
        return request.user == review.user
