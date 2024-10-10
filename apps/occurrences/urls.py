from django.urls import path

from apps.occurrences.views import (
	OccurrenceCountView,
	OccurrenceCRUDView,
	OccurrenceListView,
	OccurrenceCountByTaxonMonthView,
	OccurrenceCountByTaxonYearView,
	OccurrenceCountBySourceView,
	OccurrenceCountByTaxonAndChildrenView,
)

app_name = "occurrences"
urlpatterns = [
	path("", OccurrenceCRUDView.as_view(), name="occurrence_crud"),
	path("/list", OccurrenceListView.as_view(), name="occurrence_list"),
	path("/list/count", OccurrenceCountView.as_view(), name="occurrence_list_count"),
	path("/list/stats/month", OccurrenceCountByTaxonMonthView.as_view(), name="occurrence_month_stats"),
	path("/list/stats/year", OccurrenceCountByTaxonYearView.as_view(), name="occurrence_year_stats"),
	path("/list/stats/source", OccurrenceCountBySourceView.as_view(), name="occurrence_source_stats"),
	path("/list/stats/children", OccurrenceCountByTaxonAndChildrenView.as_view(), name="occurrence_children_stats"),
]
