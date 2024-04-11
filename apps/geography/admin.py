from django.contrib import admin

from apps.geography.models import GeographicLevel


class BaseTaxonLevelAdmin(admin.ModelAdmin):
	list_filter = ['rank']
	search_fields = ['name', 'gid']
	list_display = ['name', 'gid', 'rank']


admin.site.register(GeographicLevel,  BaseTaxonLevelAdmin)