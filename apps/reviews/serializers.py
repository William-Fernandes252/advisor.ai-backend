from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.papers.models import Paper
from apps.papers.serializers import PaperListSerializer
from apps.reviews import models
from apps.users.serializers import UserSerializer


class ReviewListSerializer(serializers.ModelSerializer):
    """Serializer for review list and create operations."""

    id = serializers.UUIDField(source="uuid", read_only=True)
    paper: serializers.SlugRelatedField = serializers.SlugRelatedField(
        "uuid", queryset=Paper.objects.all()
    )
    user: serializers.SlugRelatedField = serializers.SlugRelatedField(
        "uuid", queryset=get_user_model().objects.all()
    )
    by = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = models.Review
        exclude = ["active", "uuid"]


class ReviewDetailSerializer(serializers.ModelSerializer):
    """Serializer for review retrieve operations."""

    id = serializers.UUIDField(source="uuid", read_only=True)
    user = UserSerializer(read_only=True)
    paper = PaperListSerializer(read_only=True)

    class Meta:
        model = models.Review
        exclude = ["active", "uuid"]
