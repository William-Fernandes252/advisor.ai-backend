from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.exports import models


class ExportContentTypeListFilter(admin.filters.SimpleListFilter):
    title = _("content type")

    parameter_name = "content_type"

    def lookups(self, request, model_admin):
        return (
            models.Export.objects.values_list("content_type", "content_type__model")
            .order_by("content_type")
            .distinct("content_type")
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type=self.value())
        return queryset


@admin.register(models.Export)
class ExportAdmin(admin.ModelAdmin):
    list_display = ["filename", "created", "content_type", "latest"]
    list_filter = ["latest", ExportContentTypeListFilter, "created"]
    search_fields = ["id"]
