from django.contrib import admin
from django.db.models.query import QuerySet

from apps.ml import models


@admin.register(models.Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ["filename", "type", "latest", "created"]
    list_filter = ["type", "latest", "created"]
    search_fields = ["filename", "type"]
    readonly_fields = ["created", "modified"]
    fieldsets = (
        (None, {"fields": ("file", "type", "params", "validation_results")}),
        ("Metadata", {"fields": ("latest", "created", "modified")}),
    )
    actions = ["make_latest"]

    @admin.action(description="Make latest")
    def make_latest(self, request, queryset: QuerySet):
        """Make the selected models the latest."""
        queryset.update(latest=True)
