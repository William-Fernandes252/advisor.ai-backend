from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    help = "Create papers suggestions for users"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "model",
            nargs="?",
            default="svd",
            type=str,
            help="The model type to train.",
        )
        parser.add_argument(
            "--start",
            default=0,
            type=int,
            help="The paper to start.",
        )
        parser.add_argument(
            "--offset",
            default=50,
            type=int,
            help="The papers batch size.",
        )
        parser.add_argument(
            "--max",
            default=250,
            type=int,
            help="The number of papers to suggest.",
        )
        parser.add_argument(
            "--reuse-suggestions-up-to-days",
            type=int,
            default=7,
            help="The number of days to consider current suggestions as still valid.",
        )

    def handle(self, *args, **options):
        from apps.papers.tasks import batch_create_papers_suggestions

        batch_create_papers_suggestions(
            model_type=options["model"],
            start=options["start"],
            offset=options["offset"],
            max_papers=options["max"],
            use_suggestions_up_to_days=options["reuse_suggestions_up_to_days"],
        )

        self.stdout.write(
            self.style.SUCCESS("Successfully created new papers suggestions.")
        )
