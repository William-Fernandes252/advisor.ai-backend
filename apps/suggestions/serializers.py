from rest_access_policy import FieldAccessMixin
from rest_framework import serializers

from apps.papers.serializers import PaperListSerializer
from apps.suggestions import models, permissions


class SuggestionSerializer(FieldAccessMixin, serializers.ModelSerializer):
    """Suggestions serializer."""

    paper: PaperListSerializer = PaperListSerializer(read_only=True)
    user: serializers.SlugRelatedField = serializers.SlugRelatedField(
        "uuid", read_only=True
    )
    review: serializers.SlugRelatedField = serializers.SlugRelatedField(
        "uuid", read_only=True
    )

    class Meta:
        model = models.Suggestion
        exclude = ["active"]
        read_only_fields = ["user"]
        access_policy = permissions.SuggestionAccessPolicy
