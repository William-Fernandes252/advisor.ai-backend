from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create fake reviews for testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "count", type=int, help="The number of reviews to be created.", default=10
        )

    def handle(self, *args, **options):
        from apps.reviews.tasks import generate_fake_reviews

        count = options["count"]
        result = generate_fake_reviews(count)

        self.stdout.write(self.style.SUCCESS(f"{result} reviews created."))
