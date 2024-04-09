from django.urls import path, include

urlpatterns = [
	path('v1/', include('apps.API.v1.urls')),
]