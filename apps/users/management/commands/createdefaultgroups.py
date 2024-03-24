from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Create default groups for the application."""

    help = "Create default groups for the application."

    def handle(self, *args, **options):
        """Create default groups for the application.

        Args:
        ----
            *args: Not used.
            **options: Not used.

        """
        from django.contrib.auth.models import Group

        from apps.users.models import Group as UserGroup

        try:
            for group in UserGroup:
                Group.objects.get_or_create(name=group.value)
        except Exception as e:  # noqa: BLE001
            self.stdout.write(self.style.ERROR(str(e)))

        self.stdout.write(self.style.SUCCESS("Default groups created successfully."))
