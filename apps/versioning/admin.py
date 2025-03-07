from django.contrib import admin

from apps.versioning.models import Batch, Source, Basis, OriginId

admin.site.register(Batch)


class SourceAdmin(admin.ModelAdmin):
	search_fields = ["source_type"]
	list_display = ["basis", "data_type", "source_type", "extraction_method", "url"]
	list_filter = ["data_type"]


admin.site.register(Source, SourceAdmin)


class BasisAdmin(admin.ModelAdmin):
	search_fields = ["internal_name"]
	list_display = ["internal_name", "acronym", "url", "description", "citation"]
	list_filter = ["acronym"]


admin.site.register(Basis, BasisAdmin)


class OriginIdAdmin(admin.ModelAdmin):
	search_fields = ["external_id"]
	list_filter = ["source"]


admin.site.register(OriginId, OriginIdAdmin)
