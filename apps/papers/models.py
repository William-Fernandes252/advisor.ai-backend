from decimal import Decimal
from uuid import uuid4

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from slugify import slugify

from apps.papers import managers
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
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate a slug for the keyword."""
        return slugify(name)


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
    reviews_average = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    reviews_count = models.PositiveIntegerField(blank=True, null=True)
    last_reviews_update = models.DateTimeField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    index = models.BigIntegerField(
        help_text="Position index for embeddings", blank=True, null=True
    )

    objects = managers.PaperManager()

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

    def get_absolute_url(self) -> str:
        return reverse("paper-detail", kwargs={"pk": self.pk})

    def get_reviews_average(self) -> Decimal | None:
        """Calculates the reviews average."""
        return self.reviews.average()

    def get_reviews_count(self) -> int:
        """Calculates the number of reviews for the movie."""
        return self.reviews.count()

    def update_reviews(
        self, average: Decimal | None = None, count: int | None = None, save=None
    ) -> None:
        """Update the reviews data of the paper.

        Args:
            average (Decimal | None, optional): The updated reviews average.
            If none is provided, it will be calculated. Defaults to None.
            count (int | None, optional): The updated reviews count.
            If none is provided, it will be calculated. Defaults to None.
            save (_type_, optional): If the paper should be saved after the update.
            Defaults to None.
        """
        self.reviews_average = average or self.get_reviews_average()
        self.reviews_count = count or self.get_reviews_count()
        self.score = float(self.reviews_average or 0) * self.reviews_count
        self.last_reviews_update = timezone.now()
        if save:
            self.save()
