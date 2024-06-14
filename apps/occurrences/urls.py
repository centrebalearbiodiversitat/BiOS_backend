from django.urls import path
from apps.occurrences.views import OccurrenceListView, OccurrenceCRUDView, OccurrenceCountView, OccurrenceTaxonView

urlpatterns = [
	path("", OccurrenceCRUDView.as_view()),
	path("count", OccurrenceCountView.as_view()),
	path("list", OccurrenceListView.as_view()),
	path("taxon", OccurrenceTaxonView.as_view()),
]
