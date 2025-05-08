from django.urls import path

from apps.occurrences.views import (
	OccurrenceCountView,
	OccurrenceCRUDView,
	OccurrenceListView,
	OccurrenceCountByTaxonMonthView,
	OccurrenceCountByTaxonYearView,
	OccurrenceCountBySourceView,
	OccurrenceCountByTaxonAndChildrenView,
	OccurrenceListDownloadView,
	OccurrenceMapView,
	# OccurrenceMapCountView,
)

app_name = "occurrences"
urlpatterns = [
	path("", OccurrenceCRUDView.as_view(), name="occurrence_crud"),
	path("/map", OccurrenceMapView.as_view(), name="occurrence_list"),
	# path("/map/count", OccurrenceMapCountView.as_view(), name="occurrence_list_count"),
	path("/list", OccurrenceListView.as_view(), name="occurrence_list"),
	path("/list/download", OccurrenceListDownloadView.as_view(), name="occurrence_list_download"),
	path("/list/count", OccurrenceCountView.as_view(), name="occurrence_list_count"),
	path("/stats/month", OccurrenceCountByTaxonMonthView.as_view(), name="occurrence_month_stats"),
	path("/stats/year", OccurrenceCountByTaxonYearView.as_view(), name="occurrence_year_stats"),
	path("/stats/source", OccurrenceCountBySourceView.as_view(), name="occurrence_source_stats"),
	path("/stats/children", OccurrenceCountByTaxonAndChildrenView.as_view(), name="occurrence_children_stats"),
]
