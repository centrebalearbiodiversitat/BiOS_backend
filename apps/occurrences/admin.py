from django.contrib import admin

from apps.occurrences.models import Occurrence


class OccurrenceAdmin(admin.ModelAdmin):
	fields = [
		"taxonomy",
		"voucher",
		"geographical_location",
		"collection_date_year",
		"collection_date_month",
		"collection_date_day",
		"basis_of_record",
		"sources",
		"batch",
		"decimal_latitude",
		"decimal_longitude",
		"coordinate_uncertainty_in_meters",
		"elevation",
		"depth",
	]
	autocomplete_fields = ["taxonomy", "sources"]


admin.site.register(Occurrence, OccurrenceAdmin)
