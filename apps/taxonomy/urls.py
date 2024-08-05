from django.urls import path

from apps.taxonomy.views import (
	AuthorshipCRUDView,
	TaxonChecklistView,
	TaxonChildrenCountView,
	TaxonChildrenView,
	TaxonCompositionView,
	TaxonCRUDView,
	TaxonDataCRUDView,
	TaxonDataListView,
	TaxonListView,
	TaxonParentView,
	TaxonSearchView,
	TaxonSourceView,
	TaxonSynonymView,
)

urlpatterns = [
	path("/search", TaxonSearchView.as_view()),
	path("/list", TaxonListView.as_view()),
	path("/taxon", TaxonCRUDView.as_view()),
	path("/taxon/parent", TaxonParentView.as_view()),
	path("/taxon/children", TaxonChildrenView.as_view()),
	path("/taxon/children/count", TaxonChildrenCountView.as_view()),
	path("/taxon/composition", TaxonCompositionView.as_view()),
	path("/taxon/synonyms", TaxonSynonymView.as_view()),
	path("/taxon/sources", TaxonSourceView.as_view()),
	path("/taxon/checklist", TaxonChecklistView.as_view()),
	path("/taxon/data", TaxonDataCRUDView.as_view()),
	path("/authorship", AuthorshipCRUDView.as_view()),
	path("/data/list", TaxonDataListView.as_view()),
]
