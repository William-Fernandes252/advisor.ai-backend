from rest_access_policy import AccessPolicy
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet


class UserAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["create"],
            "principal": ["admin", "anonymous"],
            "effect": "allow",
        },
        {
            "action": [
                "update",
                "partial_update",
                "destroy",
                "retrieve",
                "me",
            ],
            "principal": "authenticated",
            "effect": "allow",
            "condition": "is_self",
        },
        {
            "action": ["list"],
            "principal": ["admin", "staff", "group:operators"],
            "effect": "allow",
        },
    ]

    def is_self(self, request: Request, view: GenericViewSet, *args) -> bool:
        """Check if the user is the same as the request user."""
        user = view.get_object()
        return request.user == user
