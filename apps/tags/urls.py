from django.urls import path

from apps.tags.views import (
    DirectiveListView,
	IUCNDataListView,
	# IUCNDataListView,
	# IUCNDataCountView,
	HabitatsListView,
	# TagListView,
	# TaxonDataInvasiveView
	SystemListView,
	TaxonTagListView
)

app_name = "tags"
urlpatterns = [
    path("", TaxonTagListView.as_view(), name="taxon_tag_list"),
    path("/directive", DirectiveListView.as_view(), name="directive_list"),
	path("/habitat", HabitatsListView.as_view(), name="habitats_List"),
	path("/iucn", IUCNDataListView.as_view(), name="iucn_list"),
	path("/system", SystemListView.as_view(), name="system_list"),
    
	# path("/taxon/tags/list", IUCNDataListView.as_view(), name="data_list"),
	# path("/taxon/data/list/count", IUCNDataCountView.as_view(), name="data_count"),
	# path("/data/list", IUCNDataListView.as_view(), name="data_list"),
	# path("/taxon/data/list/count", IUCNDataCountView.as_view(), name="data_count"),
	# path("/taxon/tag", TagListView.as_view(), name="tag_list"),
	# path("/taxon/data/invasive", TaxonDataInvasiveView.as_view(), name="data_invasive")
]
