from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PapersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.papers"
    verbose_name = _("Papers")
