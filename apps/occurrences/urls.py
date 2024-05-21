from django.urls import path
from apps.occurrences.views import OccurrenceList, OccurrenceDetail, OccurrenceCount

urlpatterns = [
	path("", OccurrenceDetail.as_view()),
	path("/count", OccurrenceCount.as_view()),
	path("/list", OccurrenceList.as_view()),
]
