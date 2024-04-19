from django.core.management.base import BaseCommand

from apps.papers import models
from apps.papers.tests import factories


class Command(BaseCommand):
    help = "Create fake papers for testing purposes."

    def add_arguments(self, parser):
        parser.add_argument(
            "count", type=int, default=10, help="The number of papers to create."
        )
        parser.add_argument(
            "--authors", type=int, default=3, help="The number of authors to create."
        )
        parser.add_argument(
            "--keywords", type=int, default=50, help="The number of keywords to create."
        )
        parser.add_argument(
            "--authors-per-paper",
            type=int,
            default=1,
            help="The number of authors per paper.",
        )
        parser.add_argument(
            "--keywords-per-paper",
            type=int,
            default=5,
            help="The number of keywords per paper.",
        )

    def create_fake_authors(self, count: int):
        """Create fake authors.

        Args:
            count (int): The number of authors to create.

        Returns:
            list[models.Author]: The created authors.
        """
        return models.Author.objects.bulk_create(
            [factories.AuthorFactory.build() for _ in range(count)]
        )

    def create_fake_keywords(self, count: int):
        """Create fake keywords.

        Args:
            count (int): The number of keywords to create.

        Returns:
            list[models.Keyword]: The created keywords.
        """
        return models.Keyword.objects.bulk_create(
            [factories.KeywordFactory.build() for _ in range(count)],
        )

    def create_fake_papers(self, count: int) -> list[models.Paper]:
        """Create fake papers.

        Args:
            count (int): The number of papers to create.

        Returns:
            list[models.Paper]: The created papers.
        """
        return models.Paper.objects.bulk_create(
            [factories.PaperFactory.build() for _ in range(count)]
        )

    def handle(self, *args, **kwargs):
        papers = self.create_fake_papers(kwargs["count"])

        self.create_fake_authors(kwargs["authors"])
        self.create_fake_keywords(kwargs["keywords"])

        for paper in papers:
            paper.authors.set(
                models.Author.objects.order_by("?")[: kwargs["authors_per_paper"]]
            )
            paper.keywords.set(
                models.Keyword.objects.order_by("?")[: kwargs["keywords_per_paper"]]
            )

        self.stdout.write(self.style.SUCCESS(f"{len(papers)} papers created."))
