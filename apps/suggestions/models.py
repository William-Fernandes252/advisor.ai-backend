from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models

from apps.suggestions import managers


class Suggestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="suggestions"
    )
    value = models.FloatField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.PROTECT,
        related_name="suggestions",
        null=True,
        blank=True,
    )
    paper = models.ForeignKey(
        "papers.Paper", on_delete=models.CASCADE, related_name="suggestions"
    )
    model = models.ForeignKey("ml.Model", on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=True)

    objects: managers.SuggestionManager = managers.SuggestionManager()

    def __str__(self):
        return f"{self.user} - {self.paper}"

    @property
    def did_rate(self):
        """Returns the date when the user rated the suggested content."""
        return self.review.created if self.review else None
