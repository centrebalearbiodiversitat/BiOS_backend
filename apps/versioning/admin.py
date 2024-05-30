from django.contrib import admin

from apps.versioning.models import Batch, Source, OriginSource

admin.site.register(Batch)


class SourceAdmin(admin.ModelAdmin):
	search_fields = ["name"]
	list_display = ["name"]


admin.site.register(Source, SourceAdmin)


class OriginSourceAdmin(admin.ModelAdmin):
	search_fields = ["origin_id"]
	list_filter = ["source"]


admin.site.register(OriginSource, OriginSourceAdmin)
