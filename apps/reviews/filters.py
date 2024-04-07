from django_filters import rest_framework as filters

from apps.reviews import models


class ReviewFilter(filters.FilterSet):
    class Meta:
        model = models.Review
        fields = ["value"]
