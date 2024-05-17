from django.urls import path, include

from apps.API.views import APIStatus

urlpatterns = [
	path("taxonomy/", include("apps.taxonomy.urls")),
	path("occurrences/", include("apps.occurrences.urls")),
	path("status", APIStatus.as_view()),
]
