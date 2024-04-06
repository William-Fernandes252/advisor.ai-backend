from rest_access_policy import AccessViewSetMixin
from rest_framework import mixins, viewsets
from rest_framework_extensions.mixins import DetailSerializerMixin

from apps.reviews import filters, models, permissions, serializers


class ReviewViewSet(
    AccessViewSetMixin,
    DetailSerializerMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """List, create, retrieve and delete paper reviews."""

    queryset = models.Review.objects.all().prefetch_related("user")
    queryset_detail = models.Review.objects.all().prefetch_related("paper", "user")
    lookup_field = "uuid"
    serializer_class = serializers.ReviewListSerializer
    serializer_detail_class = serializers.ReviewDetailSerializer
    access_policy = permissions.ReviewAccessPolicy
    filterset_class = filters.ReviewFilter
    ordering_fields = ["value", "created"]
