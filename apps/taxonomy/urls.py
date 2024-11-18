from django.urls import path

from apps.taxonomy.views import (
	TaxonSearchView,
	TaxonListView,
	TaxonCountView,
	TaxonCRUDView,
	TaxonParentView,
	TaxonChildrenView,
	TaxonChildrenCountView,
	TaxonomicLevelDescendantsCountView,
	TaxonCompositionView,
	TaxonSynonymView,
	TaxonSourceView,
	TaxonChecklistView,
	IUCNDataCRUDView,
	IUCNDataListView,
	IUCNDataCountView,
	HabitatsView,
	TagCRUDView,
	AuthorshipCRUDView,
)

app_name = "taxonomy"
urlpatterns = [
	path("/search", TaxonSearchView.as_view(), name="search"),
	path("/list", TaxonListView.as_view(), name="list"),
	path("/list/count", TaxonCountView.as_view(), name="list_count"),
	path("/taxon", TaxonCRUDView.as_view(), name="taxon_crud"),
	path("/taxon/parent", TaxonParentView.as_view(), name="taxon_parent"),
	path("/taxon/children", TaxonChildrenView.as_view(), name="taxon_children"),
	path("/taxon/children/count", TaxonChildrenCountView.as_view(), name="taxon_children_count"),
	path("/taxon/composition", TaxonCompositionView.as_view(), name="taxon_composition"),
	path("/taxon/descendants/count", TaxonomicLevelDescendantsCountView.as_view(), name="taxon_descendants_count"),
	path("/taxon/synonyms", TaxonSynonymView.as_view(), name="taxon_synonyms"),
	path("/taxon/sources", TaxonSourceView.as_view(), name="taxon_sources"),
	path("/taxon/checklist", TaxonChecklistView.as_view(), name="taxon_checklist"),
	path("/taxon/data", IUCNDataCRUDView.as_view(), name="data_crud"),
	path("/taxon/data/list", IUCNDataListView.as_view(), name="data_list"),
	path("/taxon/data/list/count", IUCNDataCountView.as_view(), name="data_count"),
	path("/taxon/data/habitats", HabitatsView.as_view(), name="data_habitats"),
	path("/taxon/tag", TagCRUDView.as_view(), name="tag_crud"),
	path("/authorship", AuthorshipCRUDView.as_view(), name="authorship_crud"),
]
