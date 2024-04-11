import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    help = "Train a surprise model using the latest exported datasets."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "model",
            nargs="?",
            default=settings.DEFAULT_MODEL_TYPE,
            type=str,
            help="The model type to train.",
        )
        parser.add_argument(
            "--params",
            default=None,
            type=str,
            help="The training parameters."
            " If not provided, the default parameters will be used.",
        )

    def handle(self, *args, **kwargs):
        from apps.papers.tasks import train_and_export_new_model

        model_type = kwargs["model"]
        try:
            params = json.loads(kwargs["params"]) if kwargs["params"] else None
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR("Invalid JSON format for the parameters.")
            )
            return

        train_and_export_new_model(model_type, params)

        self.stdout.write(self.style.SUCCESS("Successfully trained the model."))
