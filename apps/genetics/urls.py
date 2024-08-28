from django.urls import path

from .views import (
	MarkerCRUDView,
	MarkerSearchView,
	MarkerListView,
    MarkerCountView,
	SequenceCRUDView,
	SequenceCountView,
	SequenceListView,
	SequenceSearchView,
)

app_name = "genetics"
urlpatterns = [
	path("/marker", MarkerCRUDView.as_view(), name="marker_crud"),
	path("/marker/search", MarkerSearchView.as_view(), name="marker_search"),
	path("/marker/list", MarkerListView.as_view(), name="marker_list"),
    path("/marker/list/count", MarkerCountView.as_view(), name="marker_list_count"),
	path("/sequence", SequenceCRUDView.as_view(), name="sequence_crud"),
	path("/sequence/search", SequenceSearchView.as_view(), name="sequence_search"),
	path("/sequence/list", SequenceListView.as_view(), name="sequence_list"),
	path("/sequence/list/count", SequenceCountView.as_view(), name="sequence_list_count"),
]
