from django.urls import path

from apps.taxonomy.views import TaxonSearch, TaxonList, TaxonCRUD, TaxonParent, TaxonChildren

urlpatterns = [
	path('search', TaxonSearch.as_view()),
	path('list', TaxonList.as_view()),
	path('taxon/<int:id>', TaxonCRUD.as_view()),
	path('taxon/<int:id>/parent', TaxonParent.as_view()),
	path('taxon/<int:id>/children', TaxonChildren.as_view()),
	# TaxonomicLevel.objects.all().values('authorship__name').annotate(total=Count('authorship__name')).order_by('-total')
]
