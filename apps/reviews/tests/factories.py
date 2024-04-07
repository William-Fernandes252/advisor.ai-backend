from factory import Faker, SubFactory, fuzzy
from factory.django import DjangoModelFactory

from apps.reviews.models import Review


class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review

    paper = SubFactory("apps.papers.tests.factories.PaperFactory")
    user = SubFactory("apps.users.tests.factories.UserFactory")
    value = fuzzy.FuzzyChoice(Review.ValueChoices.values)
    comment = Faker("text")
    active = True
