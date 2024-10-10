from django.urls import path

from apps.occurrences.views import OccurrenceCountView, OccurrenceCRUDView, OccurrenceListView, OccurrenceListDownloadView

app_name = "occurrences"
urlpatterns = [
	path("", OccurrenceCRUDView.as_view(), name="occurrence_crud"),
	path("/list", OccurrenceListView.as_view(), name="occurrence_list"),
	path("/list/download", OccurrenceListDownloadView.as_view(), name="occurrence_list_download"),
	path("/list/count", OccurrenceCountView.as_view(), name="occurrence_list_count"),
]
