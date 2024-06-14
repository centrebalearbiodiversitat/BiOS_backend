from django.urls import path

from apps.taxonomy.views import (
	TaxonSearchView,
	TaxonListView,
	TaxonCRUDView,
	TaxonParentView,
	TaxonChildrenView,
	TaxonSynonymView,
	AuthorshipCRUDView
)

urlpatterns = [
	path("search", TaxonSearchView.as_view()),
	path("list", TaxonListView.as_view()),
	path("taxon", TaxonCRUDView.as_view()),
	path("taxon/parent", TaxonParentView.as_view()),
	path("taxon/children", TaxonChildrenView.as_view()),
	path("taxon/synonym", TaxonSynonymView.as_view()),
	path("authorship", AuthorshipCRUDView.as_view()),
]
