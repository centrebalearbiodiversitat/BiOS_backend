from django.urls import path, include

urlpatterns = [
	path("/geography", include("apps.geography.urls")),
	path("/genetics", include("apps.genetics.urls")),
	path("/occurrences", include("apps.occurrences.urls")),
	path("/tags", include("apps.tags.urls")),
	path("/taxonomy", include("apps.taxonomy.urls")),
	path("/versioning", include("apps.versioning.urls")),
]
