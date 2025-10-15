from django.contrib import admin

from apps.genetics.models import Marker, Sequence
from common.utils.admin import ReadOnlyBatch


class MarkerAdmin(ReadOnlyBatch):
	search_fields = ["unidecode_name"]
	readonly_fields = ["sources"]
	autocomplete_fields = ["synonyms"]


class SequenceAdmin(ReadOnlyBatch):
	readonly_fields = ["occurrence"]
	autocomplete_fields = ["sources", "markers"]


admin.site.register(Marker, MarkerAdmin)
admin.site.register(Sequence, SequenceAdmin)
