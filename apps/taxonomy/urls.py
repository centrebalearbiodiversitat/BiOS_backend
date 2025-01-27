from django.urls import path

from apps.taxonomy.views import (
	TaxonSearchView,
	TaxonListView,
	TaxonCountView,
	TaxonCRUDView,
	TaxonParentView,
	TaxonChildrenView,
	TaxonChildrenCountView,
	TaxonBrotherView,
	TaxonomicLevelDescendantsCountView,
	TaxonCompositionView,
	TaxonSynonymView,
	TaxonSourceView,
	TaxonChecklistView,
	AuthorshipCRUDView,
	TaxonListCSVView,
)

app_name = "taxonomy"
urlpatterns = [
	path("/search", TaxonSearchView.as_view(), name="search"),
	path("/list", TaxonListView.as_view(), name="list"),
	path("/list/count", TaxonCountView.as_view(), name="list_count"),
	path("/list/csv", TaxonListCSVView.as_view(), name="list_count"),
	path("/taxon", TaxonCRUDView.as_view(), name="taxon_crud"),
	path("/taxon/parent", TaxonParentView.as_view(), name="taxon_parent"),
	path("/taxon/children", TaxonChildrenView.as_view(), name="taxon_children"),
	path("/taxon/children/count", TaxonChildrenCountView.as_view(), name="taxon_children_count"),
	path("/taxon/brother", TaxonBrotherView.as_view(), name="taxon_brother"),
	path("/taxon/descendants/count", TaxonomicLevelDescendantsCountView.as_view(), name="taxon_descendants_count"),
	path("/taxon/composition", TaxonCompositionView.as_view(), name="taxon_composition"),
	path("/taxon/synonyms", TaxonSynonymView.as_view(), name="taxon_synonyms"),
	path("/taxon/sources", TaxonSourceView.as_view(), name="taxon_sources"),
	path("/taxon/checklist", TaxonChecklistView.as_view(), name="taxon_checklist"),
	path("/authorship", AuthorshipCRUDView.as_view(), name="authorship_crud"),
]
