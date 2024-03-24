import pytest
from django.core.management import call_command

from apps.users.models import User
from apps.users.tests.factories import UserFactory


@pytest.fixture()
def django_db_setup(django_db_setup, django_db_blocker):  # noqa: PT004
    """Django database setup fixture.

    This extends the default behavior by adding the creation of default groups
    """
    with django_db_blocker.unblock():
        call_command("createdefaultgroups")


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    """Set the faker locales."""
    return ["en_US", "pt_BR"]


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
    """Set the faker seed."""
    return 12345


@pytest.fixture()
def user(db) -> User:
    """Create a user for testing."""
    return UserFactory.create()


@pytest.fixture()
def admin(user: User) -> User:
    """Create a test user."""
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath
