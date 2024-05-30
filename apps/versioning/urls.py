from django.urls import path

from apps.versioning.views import SourceView, SourceList, OriginSourceView

urlpatterns = [
	path("source", SourceView.as_view()),
	path("source/list", SourceList.as_view()),
	path("origin_source", OriginSourceView.as_view())
]
