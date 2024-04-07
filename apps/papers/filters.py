from django_filters import rest_framework as filters

from apps.papers import models, querysets


class PaperFilter(filters.FilterSet):
    """Filter for the Paper model."""

    title = filters.CharFilter(lookup_expr="icontains")
    authors = filters.ModelMultipleChoiceFilter(
        field_name="authors__name",
        to_field_name="name",
        queryset=models.Author.objects.all(),
    )
    country = filters.CharFilter(field_name="location__country")
    keywords = filters.ModelMultipleChoiceFilter(
        field_name="keywords__name",
        to_field_name="name",
        queryset=models.Keyword.objects.all(),
        conjoined=True,
    )
    published = filters.DateTimeFromToRangeFilter()
    search = filters.CharFilter(method="search_for_papers")

    class Meta:
        model = models.Paper
        fields = ["title", "authors", "location", "keywords"]

    def search_for_papers(
        self, queryset: querysets.PaperQuerySet, name: str, value: str
    ):
        """Search for papers."""
        return queryset.search(value)
