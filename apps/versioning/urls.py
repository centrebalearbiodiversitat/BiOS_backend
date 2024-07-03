from django.urls import path

from apps.versioning.views import (
	SourceSearchView,
	SourceCRUDView,
	SourceListView,
	OriginSourceCRUDView,
)

urlpatterns = [
	path("/source", SourceCRUDView.as_view()),
	path("/source/search", SourceSearchView.as_view()),
	path("/source/list", SourceListView.as_view()),
	path("/origin", OriginSourceCRUDView.as_view()),
]
