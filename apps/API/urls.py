from django.urls import path, include

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="CBB API",
        default_version='v1',
        description="Documentation for our API usage",
        terms_of_service="",
        contact=openapi.Contact(email="centre.balear@uib.cat"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny,],
)

urlpatterns = [
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('v1/', include('apps.API.v1.urls')),
]
