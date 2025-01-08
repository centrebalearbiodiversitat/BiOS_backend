from django.urls import path

from apps.versioning.views import (
	OriginIdCRUDView,
	SourceCRUDView,
	SourceListView,
	SourceCountView,
	SourceSearchView,
)

app_name = "versioning"
urlpatterns = [
	path("/source", SourceCRUDView.as_view(), name="source_crud"),
	path("/source/search", SourceSearchView.as_view(), name="source_search"),
	path("/source/list", SourceListView.as_view(), name="source_list"),
	path("/source/list/count", SourceCountView.as_view(), name="source_list_count"),
	path("/origin", OriginIdCRUDView.as_view(), name="os_crud"),
]
