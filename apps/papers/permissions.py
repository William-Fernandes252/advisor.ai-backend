from rest_access_policy import AccessPolicy


class PaperAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": ["admin", "group:operators"],
            "effect": "allow",
        },
    ]
