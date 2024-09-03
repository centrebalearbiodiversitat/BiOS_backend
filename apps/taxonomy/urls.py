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

app_name = "taxonomy"
urlpatterns = [
	path("/search", TaxonSearchView.as_view(), name="search"),
	path("/list", TaxonListView.as_view(), name="list"),
	path("/taxon", TaxonCRUDView.as_view(), name="taxon_crud"),
	path("/taxon/parent", TaxonParentView.as_view(), name="taxon_parent"),
	path("/taxon/children", TaxonChildrenView.as_view(), name="taxon_children"),
	path("/taxon/children/count", TaxonChildrenCountView.as_view(), name="taxon_children_count"),
	path("/taxon/composition", TaxonCompositionView.as_view(), name="taxon_composition"),
	path("/taxon/synonyms", TaxonSynonymView.as_view(), name="taxon_synonyms"),
	path("/taxon/sources", TaxonSourceView.as_view(), name="taxon_sources"),
	path("/taxon/checklist", TaxonChecklistView.as_view(), name="taxon_checklist"),
	path("/taxon/data", TaxonDataCRUDView.as_view(), name="data_crud"),
	path("/authorship", AuthorshipCRUDView.as_view(), name="authorship_crud"),
	path("/data/list", TaxonDataListView.as_view(), name="data_list"),
]
