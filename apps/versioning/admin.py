from django.contrib import admin

from apps.versioning.models import Batch, Source, Module, OriginId

admin.site.register(Batch)


class ModuleAdmin(admin.ModelAdmin):
	search_fields = ["source_type"]
	list_display = ["source_type", "extraction_method", "data_type", "url"]
	list_filter = ["data_type"]


admin.site.register(Module, ModuleAdmin)

class SourceAdmin(admin.ModelAdmin):
	search_fields = ["name"]
	list_display = [
				"name",
				"acronym",
				"url",
				"description",
				"citation" ]
	list_filter = ["acronym"]
	autocomplete_fields = ["authors"]


admin.site.register(Source, SourceAdmin)

class OriginIdAdmin(admin.ModelAdmin):
	search_fields = ["external_id"]
	list_filter = ["module"]


admin.site.register(OriginId, OriginIdAdmin)
