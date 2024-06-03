from django.urls import path
from .views import GeographicLevelIdView, GeographicLevelDetailView, GeographicLevelListView, GeographicLevelParent, GeographicLevelChildren

urlpatterns = [
	path("/search", GeographicLevelDetailView.as_view()),
	path("/list", GeographicLevelListView.as_view()),
	path("/level", GeographicLevelIdView.as_view()),
	path("/level/parent", GeographicLevelParent.as_view()),
	path("/level/children", GeographicLevelChildren.as_view()),
]
