from django.urls import path

from .views import GeographicLevelChildren, GeographicLevelDetailView, GeographicLevelIdView, GeographicLevelListView, GeographicLevelCountView, GeographicLevelParent

app_name = "geography"
urlpatterns = [
	path("/search", GeographicLevelDetailView.as_view(), name="geo_search"),
	path("/list", GeographicLevelListView.as_view(), name="geo_list"),
    path("/list/count", GeographicLevelCountView.as_view(), name="geo_list_count"),
	path("/level", GeographicLevelIdView.as_view(), name="geo_crud"),
	path("/level/parent", GeographicLevelParent.as_view(), name="geo_level_parent"),
	path("/level/children", GeographicLevelChildren.as_view(), name="geo_level_children"),
]
