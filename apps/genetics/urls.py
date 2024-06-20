from django.urls import path
from .views import (
	GeneCRUDView,
	GeneDetailView,
	GeneListView,
	ProductCRUDView,
	ProductDetailView,
	ProductListView,
	ProducesCRUDView,
	ProducesListView,
	SequenceCRUDView,
	SequenceListView,
	TaxonGeneticView,
	TaxonGeneticCountView,
	SequenceSearchView,
)

urlpatterns = [
	path("/gene", GeneCRUDView.as_view()),
	path("/gene/search", GeneDetailView.as_view()),
	path("/gene/list", GeneListView.as_view()),
	path("/product", ProductCRUDView.as_view()),
	path("/product/search", ProductDetailView.as_view()),
	path("/product/list", ProductListView.as_view()),
	path("/produces", ProducesCRUDView.as_view()),
	path("/produces/list", ProducesListView.as_view()),
	path("/sequences", SequenceCRUDView.as_view()),
	path("/sequences/search", SequenceSearchView.as_view()),
	path("/sequences/list", SequenceListView.as_view()),
	path("/sequences/taxon", TaxonGeneticView.as_view()),
	path("/sequences/taxon/count", TaxonGeneticCountView.as_view()),
]
