from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Update papers reviews data."

    def add_arguments(self, parser):
        parser.add_argument(
            "count",
            nargs="?",
            type=int,
            help="Number of papers to update",
            default=None,
        )
        parser.add_argument(
            "--all",
            action="store_true",
            default=False,
            help="Update all the papers in the database",
        )

    def handle(self, *args, **kwargs):
        from apps.papers.tasks import update_papers_reviews

        update_all = kwargs["all"]
        count = kwargs["count"]
        try:
            updated = update_papers_reviews(update_all, count)
            self.stdout.write(
                self.style.SUCCESS(f"Ratings of {updated} papers updated successfully")
            )
        except Exception as exc:  # noqa: BLE001
            self.stdout.write(self.style.ERROR(str(exc)))
