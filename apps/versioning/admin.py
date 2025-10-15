from django.contrib import admin

from apps.versioning.models import Batch, Source, Basis, OriginId
from common.utils.admin import ReadOnlyBatch

admin.site.register(Batch)


class SourceAdmin(ReadOnlyBatch):
	list_display = ["basis", "data_type", "extraction_method", "url"]
	list_filter = ["data_type"]


admin.site.register(Source, SourceAdmin)


class BasisAdmin(ReadOnlyBatch):
	search_fields = ["internal_name"]
	list_display = ["internal_name", "type", "acronym", "url"]
	list_filter = []


admin.site.register(Basis, BasisAdmin)


class OriginIdAdmin(admin.ModelAdmin):
	search_fields = ["external_id"]
	list_filter = ["source"]
	list_display = ["external_id", "source"]


admin.site.register(OriginId, OriginIdAdmin)
