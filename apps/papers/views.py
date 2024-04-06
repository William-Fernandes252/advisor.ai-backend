from rest_access_policy import AccessViewSetMixin
from rest_framework import viewsets
from rest_framework_extensions.mixins import DetailSerializerMixin

from apps.papers import filters, models, permissions, serializers


class AuthorViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    """Get information about the authors covered by the platform."""

    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    access_policy = permissions.PaperAccessPolicy


class PaperViewSet(AccessViewSetMixin, DetailSerializerMixin, viewsets.ModelViewSet):
    """List, search and and get details about the latest papers
    published on online libraries."""

    queryset = models.Paper.objects.all()
    lookup_field = "uuid"
    serializer_class = serializers.PaperListSerializer
    serializer_detail_class = serializers.PaperDetailSerializer
    access_policy = permissions.PaperAccessPolicy
    filterset_class = filters.PaperFilter
    ordering_fields = ["-published", "title"]
