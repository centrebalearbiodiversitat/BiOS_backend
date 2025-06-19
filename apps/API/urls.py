from apps.API.views import APIStatus
from django.conf import settings
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
	def get_schema(self, request=None, public=False):
		schema = super().get_schema(request, public)
		if settings.DEBUG:
			schema.schemes = ["http"]
		else:
			schema.schemes = ["https"]
		return schema


schema_view = get_schema_view(
	openapi.Info(
		title="Balearica API",
		default_version="v1",
		description="Documentation for our API usage",
		terms_of_service="",
		contact=openapi.Contact(email="centrebalear@uib.cat"),
		license=openapi.License(name="BSD License"),
	),
	public=True,
	permission_classes=[permissions.AllowAny],
	generator_class=BothHttpAndHttpsSchemaGenerator,
)


urlpatterns = [
	re_path("/docs/?$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
	path("/v1", include("apps.API.v1.urls")),
	path("/status", APIStatus.as_view()),
]
