from django_filters import rest_framework as filters

from apps.papers import models, querysets


class PaperFilter(filters.FilterSet):
    """Filter for the Paper model."""

    title = filters.CharFilter(
        lookup_expr="icontains", label="Title", help_text="Filter by title."
    )
    authors = filters.ModelMultipleChoiceFilter(
        field_name="authors__name",
        to_field_name="name",
        queryset=models.Author.objects.all(),
        label="Authors",
        help_text="Filter by a list of authors.",
    )
    country = filters.CharFilter(
        field_name="location__country", label="Country", help_text="Filter by country."
    )
    keywords = filters.ModelMultipleChoiceFilter(
        field_name="keywords__name",
        to_field_name="name",
        queryset=models.Keyword.objects.all(),
        conjoined=True,
        help_text="Filter by a set of keywords."
        " Only papers that have all the keywords will be returned.",
    )
    published = filters.DateTimeFromToRangeFilter(
        label="Publishing date range",
        help_text="Filter papers published on the specified period.",
    )
    search = filters.CharFilter(
        method="search_for_papers",
        label="Search",
        help_text="Search by the papers content.",
    )

    class Meta:
        model = models.Paper
        fields = ["title", "authors", "keywords", "search", "country", "published"]

    def search_for_papers(
        self, queryset: querysets.PaperQuerySet, name: str, value: str
    ):
        """Search for papers."""
        return queryset.search(value)
