from rest_access_policy import AccessPolicy


class PaperAccessPolicy(AccessPolicy):
    """Paper access policy."""

    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": ["suggestions"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": ["admin", "group:operators"],
            "effect": "allow",
        },
    ]
