from django.contrib import admin

from apps.geography.models import GeographicLevel


class BaseTaxonLevelAdmin(admin.ModelAdmin):
	list_filter = ['rank']


admin.site.register(GeographicLevel,  BaseTaxonLevelAdmin)