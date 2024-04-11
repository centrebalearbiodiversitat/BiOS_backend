from django.contrib import admin

from apps.geography.models import GeographicLevel


class BaseTaxonLevelAdmin(admin.ModelAdmin):
	list_filter = ['rank', 'accepted']
	search_fields = ['name', 'gid']
	list_display = ['name', 'gid', 'rank']
	filter_horizontal = ['synonyms']

	def get_queryset(self, request):
		return super().get_queryset(request)


admin.site.register(GeographicLevel,  BaseTaxonLevelAdmin)