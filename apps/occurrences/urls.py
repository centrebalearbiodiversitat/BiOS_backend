from django.urls import path

from apps.occurrences.views import (
    OccurrenceCountView,
    OccurrenceCRUDView,
    OccurrenceListView,
    OccurrenceCountByTaxonMonth,
    OccurrenceCountByTaxonYear,
    OccurrenceCountBySource,
    OccurrenceCountByTaxonAndChildren
)

app_name = "occurrences"
urlpatterns = [
	path("", OccurrenceCRUDView.as_view(), name="occurrence_crud"),
	path("/list", OccurrenceListView.as_view(), name="occurrence_list"),
	path("/list/count", OccurrenceCountView.as_view(), name="occurrence_list_count"),
    path("/list/stats/month", OccurrenceCountByTaxonMonth.as_view(), name="occurrence_month_stats"),
	path("/list/stats/year", OccurrenceCountByTaxonYear.as_view(), name="occurrence_year_stats"),
	path("/list/stats/source", OccurrenceCountBySource.as_view(), name="occurrence_source_stats"),
    path("/list/stats/children", OccurrenceCountByTaxonAndChildren.as_view(), name="occurrence_children_stats")
]
