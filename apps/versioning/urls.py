from django.urls import path

from apps.versioning.views import (
    BasisCRUDView,
	BasisListView,
	BasisCountView,
	BasisSearchView,
	OriginIdCRUDView,
	SourceCRUDView,
	SourceListView,
	SourceCountView,
	SourceSearchView,
)

app_name = "versioning"
urlpatterns = [
    path("/basis", BasisCRUDView.as_view(), name="basis_crud"),
	path("/basis/list", BasisListView.as_view(), name="basis_list"),
	path("/basis/list/count", BasisCountView.as_view(), name="basis_list_count"),
	path("/basis/search", BasisSearchView.as_view(), name="basis_search"),
	path("/source", SourceCRUDView.as_view(), name="source_crud"),
	path("/source/list", SourceListView.as_view(), name="source_list"),
	path("/source/list/count", SourceCountView.as_view(), name="source_list_count"),
	path("/source/search", SourceSearchView.as_view(), name="source_search"),
	path("/origin", OriginIdCRUDView.as_view(), name="os_crud"),
]
