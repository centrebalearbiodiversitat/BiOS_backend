from django.contrib import admin

from apps.genetics.models import Marker, Sequence


class MarkerAdmin(admin.ModelAdmin):
	search_fields = ["unidecode_name"]
	autocomplete_fields = ["synonyms", "sources"]


class SequenceAdmin(admin.ModelAdmin):
	readonly_fields = ["occurrence"]
	autocomplete_fields = ["sources", "markers"]


admin.site.register(Marker, MarkerAdmin)
admin.site.register(Sequence, SequenceAdmin)
