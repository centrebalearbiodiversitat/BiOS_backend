from django.contrib import admin

from apps.occurrences.models import Occurrence


class OccurrenceAdmin(admin.ModelAdmin):
	fields = [
		"taxonomy",
		"voucher",
		"collection_date_year",
		"collection_date_month",
		"collection_date_day",
		"basis_of_record",
		"sources",
		"batch",
		"location",
		"coordinate_uncertainty_in_meters",
		"elevation",
		"depth",
	]
	autocomplete_fields = ["taxonomy", "sources"]
	search_fields = ["taxonomy__name", "voucher"]
	readonly_fields = ["location"]


admin.site.register(Occurrence, OccurrenceAdmin)
