from django.urls import path

from apps.taxonomy.views import TaxonSearch, TaxonList, TaxonCRUD, TaxonParent, TaxonChildren, AuthorshipCRUD

urlpatterns = [
	path("search", TaxonSearch.as_view()),
	path("list", TaxonList.as_view()),
	path("taxon", TaxonCRUD.as_view()),
	path("taxon/parent", TaxonParent.as_view()),
	path("taxon/children", TaxonChildren.as_view()),
	path("authorship", AuthorshipCRUD.as_view()),
	]
