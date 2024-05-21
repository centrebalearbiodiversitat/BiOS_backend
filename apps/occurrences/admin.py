from django.contrib import admin

from apps.occurrences.models import Occurrence


class OccurrenceAdmin(admin.ModelAdmin):
	autocomplete_fields = ["taxonomy", "sources"]


admin.site.register(Occurrence, OccurrenceAdmin)
