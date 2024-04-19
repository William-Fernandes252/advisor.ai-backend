from django.contrib import admin
from django.http import HttpRequest

from apps.reviews.querysets import ReviewQuerySet

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("paper", "user", "value", "created", "active")
    list_filter = ("active", "created")
    search_fields = ("user__email", "paper__title")
    ordering = ("created", "active", "user__email", "value")
    date_hierarchy = "created"
    actions = ["activate", "deactivate"]
    readonly_fields = ("created", "active")

    @admin.action(description="Activate selected ratings")
    def activate(self, request: HttpRequest, queryset: ReviewQuerySet):
        queryset.activate()

    @admin.action(description="Deactivate selected ratings")
    def deactivate(self, request: HttpRequest, queryset: ReviewQuerySet):
        queryset.deactivate()
