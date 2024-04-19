from factory import Faker, lazy_attribute_sequence, post_generation
from factory.django import DjangoModelFactory
from slugify import slugify

from apps.papers import models


class AuthorFactory(DjangoModelFactory):
    """Factory for the Author model."""

    name = Faker("name")
    uri = Faker("url")

    class Meta:
        model = models.Author


class LocationFactory(DjangoModelFactory):
    """Factory for the Location model."""

    city = Faker("city")
    state = Faker("state")
    country = Faker("country_code", representation="alpha-3")

    class Meta:
        model = models.Location


class KeywordFactory(DjangoModelFactory):
    """Factory for the Keyword model."""

    name = Faker("sentence", nb_words=2, variable_nb_words=True)

    class Meta:
        model = models.Keyword

    @lazy_attribute_sequence
    def slug(self: models.Keyword, n: int):
        """Generate a slug for the keyword."""
        return slugify(self.name + str(n))


class PaperFactory(DjangoModelFactory):
    """Factory for the Paper model."""

    title = Faker("sentence")
    abstract = Faker("text")
    published = Faker("date")
    location = LocationFactory()
    doi = Faker("isbn13")
    uri = Faker("url")
    pdf = Faker("file_path", extension="pdf")

    class Meta:
        model = models.Paper

    @post_generation
    def authors(self: models.Paper, create, extracted, **kwargs):
        """Add authors to the paper."""
        if not create:
            return

        if extracted:
            for author in extracted:
                self.authors.add(author)

    @post_generation
    def keywords(self: models.Paper, create, extracted, **kwargs):
        """Add keywords to the paper."""
        if not create:
            return

        if extracted:
            for keyword in extracted:
                self.keywords.add(keyword)
