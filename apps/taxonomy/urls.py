from django.urls import path

from apps.taxonomy.views import TaxonSearch, TaxonList, TaxonCRUD, TaxonParent, TaxonChildren

urlpatterns = [
	path("/search", TaxonSearch.as_view()),
	path("/list", TaxonList.as_view()),
	path("/taxon", TaxonCRUD.as_view()),
	path("/taxon/parent", TaxonParent.as_view()),
	path("/taxon/children", TaxonChildren.as_view()),
	# from django.db.models import Count
	# TaxonomicLevel.objects.all().values('authorship__name').annotate(total=Count('authorship__name')).order_by('-total')
]
