from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create fake users"

    def add_arguments(self, parser):
        parser.add_argument(
            "total",
            nargs="?",
            type=int,
            help="Indicates the number of users to be created",
            default=10,
        )
        parser.add_argument(
            "--show-total",
            action="store_true",
            default=False,
            help="Show the total number of users in the database after the run",
        )

    def handle(self, *args, **kwargs):
        from apps.users.models import User
        from apps.users.tests.factories import UserFactory

        total = kwargs["total"]
        try:
            User.objects.bulk_create(
                [UserFactory.build() for _ in range(total)],
                ignore_conflicts=True,
            )
        except Exception as exc:  # noqa: BLE001
            self.stdout.write(self.style.ERROR(str(exc)))

        self.stdout.write(self.style.SUCCESS(f"{total} users created successfully"))

        show_total = kwargs["show_total"]
        if show_total:
            self.stdout.write(
                self.style.WARNING(
                    f"There are {User.objects.count()} users in the database.",
                ),
            )
