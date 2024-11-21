from django.urls import path

from apps.tags.views import (
	IUCNDataCRUDView,
	# IUCNDataListView,
	# IUCNDataCountView,
	HabitatsCRUDView,
	# TagCRUDView,
  	# TaxonDataInvasiveView
	SystemCRUDView,
    TaxonTagCRUDView
)

app_name = "tags"
urlpatterns = [
    path("/habitats", HabitatsCRUDView.as_view(), name="habitats_crud"),
	path("/iucn", IUCNDataCRUDView.as_view(), name="iucn_crud"),
    path("/", TaxonTagCRUDView.as_view(), name="taxon_tag_crud",),
    path("/system", SystemCRUDView.as_view(), name="system_crud")

	# path("/taxon/tags/list", IUCNDataListView.as_view(), name="data_list"),
	# path("/taxon/data/list/count", IUCNDataCountView.as_view(), name="data_count"),
	# path("/data/list", IUCNDataListView.as_view(), name="data_list"),
	# path("/taxon/data/list/count", IUCNDataCountView.as_view(), name="data_count"),
	# path("/taxon/tag", TagCRUDView.as_view(), name="tag_crud"),
    # path("/taxon/data/invasive", TaxonDataInvasiveView.as_view(), name="data_invasive")
	
]
