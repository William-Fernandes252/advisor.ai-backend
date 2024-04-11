from typing import override

from rest_access_policy import AccessViewSetMixin
from rest_framework import mixins, viewsets
from rest_framework_extensions.mixins import DetailSerializerMixin

from apps.papers.tasks import batch_create_papers_suggestions
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

    queryset = models.Review.objects.active().prefetch_related("user")
    queryset_detail = models.Review.objects.active().prefetch_related("paper", "user")
    lookup_field = "uuid"
    serializer_class = serializers.ReviewListSerializer
    serializer_detail_class = serializers.ReviewDetailSerializer
    access_policy = permissions.ReviewAccessPolicy
    filterset_class = filters.ReviewFilter
    ordering_fields = ["value", "created"]

    def update_user_suggestions(self) -> None:
        """Update the user suggestions after some reviews are created."""
        items_rated = self.request.session.get("items_rated", 0)
        items_rated += 1
        self.request.session["items_rated"] = items_rated

        start = self.request.session.get("total_new_suggestions", 0)
        if items_rated % 5 == 0:
            batch_create_papers_suggestions.delay(
                users_ids=[self.request.user.id],
                start=start,
                offset=25,
                max=25,
                use_suggestions_up_to_days=None,
            )

    @override
    def perform_create(self, serializer) -> None:
        super().perform_create(serializer)
        self.update_user_suggestions()
