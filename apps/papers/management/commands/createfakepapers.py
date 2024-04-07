import asyncio
import asyncio.constants
import asyncio.taskgroups
import asyncio.tasks

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
            "--authors", type=int, default=1, help="The number of authors per paper."
        )
        parser.add_argument(
            "--keywords", type=int, default=3, help="The number of keywords per paper."
        )

    async def create_fake_authors(self, count: int):
        """Create fake authors.

        Args:
            count (int): The number of authors to create.

        Returns:
            list[models.Author]: The created authors.
        """
        return await models.Author.objects.abulk_create(
            [factories.AuthorFactory.build() for _ in range(count)]
        )

    async def create_fake_keywords(self, count: int):
        """Create fake keywords.

        Args:
            count (int): The number of keywords to create.

        Returns:
            list[models.Keyword]: The created keywords.
        """
        return await models.Keyword.objects.abulk_create(
            [factories.KeywordFactory.build() for _ in range(count)],
        )

    async def create_fake_papers(self, count: int):
        """Create fake papers.

        Args:
            count (int): The number of papers to create.

        Returns:
            list[models.Paper]: The created papers.
        """
        return await models.Paper.objects.abulk_create(
            [factories.PaperFactory.build() for _ in range(count)]
        )

    async def _handle(self, *args, **options):
        count = options["count"]

        for paper in await self.create_fake_papers(count):
            async with asyncio.taskgroups.TaskGroup() as tg:
                authors_task = tg.create_task(
                    self.create_fake_authors(options["authors"])
                )
                keywords_task = tg.create_task(
                    self.create_fake_keywords(options["keywords"])
                )
            async with asyncio.taskgroups.TaskGroup() as tg:
                tg.create_task(
                    models.Paper.authors.through.objects.abulk_create(
                        [
                            models.Paper.authors.through(paper=paper, author=author)
                            for author in await authors_task
                        ]
                    )
                )
                tg.create_task(
                    models.Paper.keywords.through.objects.abulk_create(
                        [
                            models.Paper.keywords.through(paper=paper, keyword=keyword)
                            for keyword in await keywords_task
                        ]
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"{count} papers created."))

    def handle(self, *args, **options):
        return asyncio.run(self._handle(*args, **options))
