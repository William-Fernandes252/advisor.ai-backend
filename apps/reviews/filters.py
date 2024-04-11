from django_filters import rest_framework as filters

from apps.reviews import models


class ReviewFilter(filters.FilterSet):
    """Filter for the Review model."""

    class Meta:
        model = models.Review
        fields = ["value"]
