from typing import Self
from uuid import uuid4

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from slugify import slugify

from common.models import UuidModel


class Author(TimeStampedModel, UuidModel, models.Model):
    """Model to represent the authors of a paper."""

    name = models.CharField(max_length=255)
    uri = models.URLField(
        _("Source of the author's information"),
        help_text=_("Could be a ORCID link, a resume on Lattes etc."),
        blank=True,
    )

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")
        indexes = [
            *UuidModel.Meta.indexes,
            models.Index(fields=["name"], name="author_name_index"),
        ]

    def __str__(self) -> str:
        return self.name


class Location(TimeStampedModel, models.Model):
    """Model to represent the location of a published paper."""

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    country = models.CharField(
        max_length=3,
        help_text=_("The ISO 3166-1 alfa-3 code of the country"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        indexes = [
            models.Index(fields=["country"], name="country_index"),
            models.Index(fields=["city", "country", "state"], name="location_index"),
        ]

    def __str__(self) -> str:
        """Return a string representation of the location."""
        return f"{self.city}, {self.state} - {self.country}"


class Keyword(TimeStampedModel, models.Model):
    """Model to represent the keywords of a paper."""

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        _("Slug"), help_text=_("The slug of the keyword"), unique=True, editable=False
    )

    class Meta:
        verbose_name = _("Keyword")
        verbose_name_plural = _("Keywords")
        indexes = [models.Index(fields=["name"], name="keyword_name_index")]

    def __str__(self) -> str:
        """Return a string representation of the keyword."""
        return self.name

    def save(self, *args, **kwargs):
        """Override the save method to generate the slug."""
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate a slug for the keyword."""
        return slugify(name)


class PaperQuerySet(models.QuerySet):
    def search(self, value: str) -> Self:
        """Search for papers.

        Args:
            query (str): The term to search for. It will be searched in the title
            and abstract of the papers.

        Returns:
            QuerySet: A queryset with the search results ordered by the
            rank of the search.
        """
        vector = SearchVector("title") + SearchVector("abstract")
        query = SearchQuery(value)
        return self.annotate(rank=SearchRank(vector, query)).order_by("-rank")


class Paper(TimeStampedModel, UuidModel, models.Model):
    """A model to represent a paper."""

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    authors = models.ManyToManyField(Author, related_name="papers")
    abstract = models.TextField()
    published = models.DateField(null=True)
    uri = models.URLField(
        _("Link to the paper"),
        help_text=_("Link to the paper in its source website"),
        blank=True,
    )
    doi = models.CharField(
        _("DOI"),
        help_text=_("The DOI (Digital Object Identifier) of the paper"),
        unique=True,
        max_length=255,
        blank=True,
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name="papers",
        null=True,
        blank=True,
    )
    keywords = models.ManyToManyField(Keyword, related_name="papers")
    pdf = models.URLField(
        _("Link to the PDF"),
        help_text=_("Link to the PDF of the paper"),
        blank=True,
    )

    objects = PaperQuerySet.as_manager()

    class Meta:
        verbose_name = _("Paper")
        verbose_name_plural = _("Papers")
        indexes = [
            *UuidModel.Meta.indexes,
            models.Index(fields=["title", "abstract"], name="search_index"),
            models.Index(fields=["-published"], name="published_index"),
        ]

    def __str__(self) -> str:
        """Return a string representation of the paper."""
        return self.title

    def get_absolute_url(self):
        return reverse("paper-detail", kwargs={"pk": self.pk})
