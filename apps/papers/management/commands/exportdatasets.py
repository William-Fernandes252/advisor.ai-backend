from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Export movies and movie ratings datasets for training models."

    def handle(self, *args, **options):
        import threading

        from apps.papers.tasks import (
            export_paper_reviews_dataset,
            export_papers_dataset,
        )

        threads = [
            threading.Thread(target=export_papers_dataset),
            threading.Thread(target=export_paper_reviews_dataset),
        ]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.stdout.write(self.style.SUCCESS("Successfully exported datasets."))
