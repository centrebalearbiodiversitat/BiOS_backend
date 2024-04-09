from django.urls import path, include

urlpatterns = [
	path('taxonomy/', include('apps.taxonomy.urls')),
]