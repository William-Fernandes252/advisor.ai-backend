from celery import shared_task

from apps.papers.models import Paper
from apps.reviews.tests.factories import ReviewFactory
from apps.users.models import User


@shared_task(name="generate_fake_reviews")
def generate_fake_reviews(count: int):
    """Generate fake reviews for papers.

    Args:
        count (int): The number of reviews to be created.

    Returns:
        int: the number of reviews created.
    """
    papers = Paper.objects.all()
    users = User.objects.all()
    reviews = [
        ReviewFactory(
            paper=papers.order_by("?").first(), user=users.order_by("?").first()
        )
        for _ in range(count)
    ]

    return len(reviews)
