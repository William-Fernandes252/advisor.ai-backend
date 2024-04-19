from django.contrib import admin

from apps.suggestions import models


@admin.register(models.Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = (
        "paper",
        "user",
        "value",
        "created",
        "did_rate",
        "active",
        "model",
    )
    list_filter = ("created", "value", "active")
    search_fields = ("user__email", "paper__title", "paper__uuid", "model__id")
    ordering = ("created", "user__email", "value")
    date_hierarchy = "created"
    readonly_fields = ("created", "model", "review", "user", "paper")
