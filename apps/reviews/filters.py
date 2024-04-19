from django_filters import rest_framework as filters

from apps.reviews import models


class ReviewFilter(filters.FilterSet):
    """Filter for the Review model."""

    paper = filters.UUIDFilter(field_name="paper__uuid")
    user = filters.UUIDFilter(field_name="user__uuid")

    class Meta:
        model = models.Review
        fields = ["value", "paper", "user"]
