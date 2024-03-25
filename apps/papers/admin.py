from django.contrib import admin

from apps.papers import models


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin class for the Author model."""

    list_display = ["name", "uri"]
    search_fields = ["name"]


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin class for the Location model."""

    list_display = ["city", "state", "country"]
    search_fields = ["city", "state", "country"]


@admin.register(models.Keyword)
class KeywordAdmin(admin.ModelAdmin):
    """Admin class for the Keyword model."""

    list_display = ["name"]
    search_fields = ["name"]


class AuthorInline(admin.TabularInline):
    """Inline for the Author model."""

    model = models.Paper.authors.through
    extra = 1


class KeywordInline(admin.StackedInline):
    """Inline for the Keyword model."""

    model = models.Paper.keywords.through
    extra = 1


@admin.register(models.Paper)
class PaperAdmin(admin.ModelAdmin):
    """Admin class for the Paper model."""

    list_display = ["title", "published"]
    search_fields = ["title", "abstract"]
    inlines = [AuthorInline, KeywordInline]
