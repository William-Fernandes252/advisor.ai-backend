from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.reviews import managers
from common.models import UuidModel


class Review(UuidModel, models.Model):
    class ValueChoices(models.IntegerChoices):
        """Rating value choices."""

        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5
        __empty__ = _("Add your review")

    value = models.SmallIntegerField(
        null=True, blank=True, choices=ValueChoices.choices
    )
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="ratings"
    )
    comment = models.TextField(blank=True)
    paper = models.ForeignKey(
        "papers.Paper", on_delete=models.CASCADE, related_name="reviews"
    )

    objects: managers.ReviewManager = managers.ReviewManager()

    class Meta:
        indexes = [*UuidModel.Meta.indexes]

    def __str__(self) -> str:
        return str(self.value)
