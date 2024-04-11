from typing import override

from rest_access_policy import AccessViewSetMixin
from rest_framework import viewsets

from apps.suggestions import models, permissions, serializers


class SuggestionViewSet(AccessViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """List, and retrieve your paper suggestions."""

    queryset = models.Suggestion.objects.all().prefetch_related("paper")
    serializer_class = serializers.SuggestionSerializer
    access_policy = permissions.SuggestionAccessPolicy
    ordering = ["-created", "-value"]

    @override
    def get_queryset(self):
        """Scope the queryset so that common users can see only their suggestions."""
        return self.access_policy.scope_queryset(self.request, super().get_queryset())
