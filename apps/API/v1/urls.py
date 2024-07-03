from django.urls import path, include

urlpatterns = [
	path("/taxonomy", include("apps.taxonomy.urls")),
	path("/occurrence", include("apps.occurrences.urls")),
	path("/geography", include("apps.geography.urls")),
	path("/genetics", include("apps.genetics.urls")),
	path("/versioning", include("apps.versioning.urls")),
]
