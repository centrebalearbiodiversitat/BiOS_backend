from django.contrib import admin

from apps.geography.models import GeographicLevel


class BaseTaxonLevelAdmin(admin.ModelAdmin):
	list_filter = ["rank", "accepted"]
	search_fields = ["unidecode_name"]
	list_display = ["name", "rank"]
	autocomplete_fields = ["synonyms"]
	exclude = ["references"]
	readonly_fields = ["location"]


admin.site.register(GeographicLevel, BaseTaxonLevelAdmin)
