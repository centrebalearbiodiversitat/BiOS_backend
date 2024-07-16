from django.urls import path
from .views import (
	GeneCRUDView,
	GeneDetailView,
	SequenceCRUDView,
	SequenceSearchView,
	SequenceListView,
	SequenceListCountView,
	MarkersListView,
)

urlpatterns = [
	path("/gene", GeneCRUDView.as_view()),
	path("/gene/search", GeneDetailView.as_view()),
	path("/gene/list", MarkersListView.as_view()),
	path("/sequence", SequenceCRUDView.as_view()),
	path("/sequence/search", SequenceSearchView.as_view()),
	path("/sequence/list", SequenceListView.as_view()),
	path("/sequence/list/count", SequenceListCountView.as_view()),
]
