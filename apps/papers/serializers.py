import pycountry
from django.utils.translation import gettext_lazy as _
from rest_access_policy import FieldAccessMixin
from rest_framework import serializers

from apps.papers import models, permissions


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for the Author model."""

    id = serializers.UUIDField(source="uuid", read_only=True)

    class Meta:
        model = models.Author
        exclude = ["created", "modified", "uuid"]


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for the Location model."""

    class Meta:
        model = models.Location
        exclude = ["created", "modified", "id"]

    def validate_country(self, value):
        """Validate the country field."""
        if not pycountry.countries.get(alpha_3=value):
            raise serializers.ValidationError(_("Invalid ISO 3166-1 alfa-3 code"))
        return value


class KeywordSerializer(serializers.ModelSerializer):
    """Serializer for the Keyword model."""

    class Meta:
        model = models.Keyword
        exclude = ["created", "modified"]


class PaperListSerializer(FieldAccessMixin, serializers.ModelSerializer):
    """Serializer for the Paper model."""

    id = serializers.UUIDField(source="uuid", read_only=True)
    keywords = serializers.SlugRelatedField(  # type: ignore[var-annotated]
        "name",
        many=True,
        queryset=models.Keyword.objects.all(),
    )
    authors = AuthorSerializer(many=True, read_only=False)
    location = LocationSerializer(read_only=False)

    class Meta:
        model = models.Paper
        exclude = ["abstract", "created", "modified", "uuid"]
        access_policy = permissions.PaperAccessPolicy

    def create(self, validated_data):
        """Create a new paper.

        It creates the authors, keywords and location if they don't exist.
        """
        authors_data = validated_data.pop("authors")
        keywords_data = validated_data.pop("keywords")
        location_data = validated_data.pop("location")

        paper = models.Paper.objects.create(**validated_data)
        for author_data in authors_data:
            author, _ = models.Author.objects.get_or_create(**author_data)
            paper.authors.add(author)

        for keyword_data in keywords_data:
            slug = models.Keyword.generate_slug(keyword_data["name"])
            keyword, _ = models.Keyword.objects.get_or_create(
                slug=slug, defaults=keyword_data
            )
            paper.keywords.add(keyword)

        location, _ = models.Location.objects.get_or_create(**location_data)
        paper.location = location

        return paper


class PaperDetailSerializer(PaperListSerializer):
    """Serializer for the Paper model."""

    class Meta:
        model = models.Paper
        fields = "__all__"
        access_policy = permissions.PaperAccessPolicy

    def update(self, instance, validated_data):
        """Update a paper."""
        authors_data = validated_data.pop("authors")
        keywords_data = validated_data.pop("keywords")
        location_data = validated_data.pop("location")

        instance = super().update(instance, validated_data)

        instance.authors.clear()
        for author_data in authors_data:
            author, _ = models.Author.objects.get_or_create(**author_data)
            instance.authors.add(author)

        instance.keywords.clear()
        for keyword_data in keywords_data:
            keyword, _ = models.Keyword.objects.get_or_create(**keyword_data)
            instance.keywords.add(keyword)

        location, _ = models.Location.objects.get_or_create(**location_data)
        instance.location = location

        return instance
