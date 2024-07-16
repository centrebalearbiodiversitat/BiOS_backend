from django.urls import path
from apps.occurrences.views import (
	OccurrenceListView,
	OccurrenceCRUDView,
	OccurrenceCountView,
)

urlpatterns = [
	path("", OccurrenceCRUDView.as_view()),
	path("/list", OccurrenceListView.as_view()),
	path("/list/count", OccurrenceCountView.as_view()),
]
