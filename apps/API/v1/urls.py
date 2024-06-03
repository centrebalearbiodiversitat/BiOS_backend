from django.urls import path, include

urlpatterns = [
	path("/taxonomy", include("apps.taxonomy.urls")),
	path("/occurrences", include("apps.occurrences.urls")),
	path("/geography", include("apps.geography.urls")),
	path("/versioning", include("apps.versioning.urls")),
]
