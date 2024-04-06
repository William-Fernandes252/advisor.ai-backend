from django.db import models


class ReviewQuerySet(models.QuerySet):
    def active(self):
        """Return only active reviews."""
        return self.filter(active=True)

    def inactive(self):
        """Return only inactive reviews."""
        return self.filter(active=False)

    def activate(self):
        """Activates the selected reviews."""
        return self.update(active=True)

    def deactivate(self):
        """Deactivates the selected reviews."""
        return self.update(active=False)

    def average(self):
        return self.aggregate(average=models.Avg("value"))["average"]
