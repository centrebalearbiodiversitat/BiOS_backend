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
	GeneticFeaturesCRUDView,
	GeneticFeaturesDetailView,
	GeneticFeaturesListView,
)

urlpatterns = [
	path("gene", GeneCRUDView.as_view()),
	path("gene/search", GeneDetailView.as_view()),
	path("gene/list", GeneListView.as_view()),
	path("product", ProductCRUDView.as_view()),
	path("product/search", ProductDetailView.as_view()),
	path("product/list", ProductListView.as_view()),
	path("produces", ProducesCRUDView.as_view()),
	path("produces/list", ProducesListView.as_view()),
	path("genetic-features", GeneticFeaturesCRUDView.as_view()),
	path("genetic-features/search", GeneticFeaturesDetailView.as_view()),
	path("genetic-features/list", GeneticFeaturesListView.as_view()),
]
