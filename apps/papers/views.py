from typing import override

from rest_access_policy import AccessViewSetMixin
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework_extensions.mixins import DetailSerializerMixin

from apps.papers import filters, models, permissions, serializers
from apps.suggestions.models import Suggestion


class AuthorViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    """Get information about the authors covered by the platform."""

    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    access_policy = permissions.PaperAccessPolicy


class PaperViewSet(AccessViewSetMixin, DetailSerializerMixin, viewsets.ModelViewSet):
    """List, search and and get details about the latest papers
    published on online libraries."""

    queryset = (
        models.Paper.objects.all()
        .select_related("location")
        .prefetch_related("authors", "keywords")
    )
    lookup_field = "uuid"
    serializer_class = serializers.PaperListSerializer
    serializer_detail_class = serializers.PaperDetailSerializer
    access_policy = permissions.PaperAccessPolicy
    filterset_class = filters.PaperFilter
    ordering_fields = ["published", "title", "score", "reviews_average"]

    def get_queryset_from_suggestions(self):
        """Get the queryset from the papers suggestions for the user."""
        suggestions_queryset = Suggestion.objects.filter(
            user=self.request.user,
            review__isnull=True,
        )

        self.request.session["total_new_suggestions"] = suggestions_queryset.count()

        if suggestions_queryset.exists():
            movies_ids = suggestions_queryset.order_by("-value").values_list(
                "paper_id", flat=True
            )
            return models.Paper.objects.order_by_ids(movies_ids)
        return models.Paper.objects.popular()

    @override
    def get_queryset(self):
        """Return the queryset for the view."""
        if self.action == "suggestions":
            return self.get_queryset_from_suggestions()
        return super().get_queryset()

    @action(detail=False, methods=["get"])
    def suggestions(self, request, *args, **kwargs):
        """Get the list of suggestions for the user."""
        return self.list(request, *args, **kwargs)
