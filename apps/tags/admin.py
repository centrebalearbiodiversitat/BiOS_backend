from django.contrib import admin

from apps.tags.models import Habitat, TaxonTag, Tag, System, IUCNData, Directive


class HabitatAdmin(admin.ModelAdmin):
	search_fields = ["name"]
	list_display = ["name"]
	fields = ["name", "sources"]
	readonly_fields = ["name"]
	autocomplete_fields = ["sources"]


admin.site.register(Habitat, HabitatAdmin)


class TagAdmin(admin.ModelAdmin):
	search_fields = ["name", "tag_type"]
	list_display = ["name", "tag_type"]
	fields = ["name", "tag_type"]


admin.site.register(Tag, TagAdmin)


class IUCNDataAdmin(admin.ModelAdmin):
	list_display = ("taxonomy", "iucn_global", "iucn_europe", "iucn_mediterranean")
	list_filter = ("iucn_global", "iucn_europe", "iucn_mediterranean")
	search_fields = ("taxonomy__name",)
	autocomplete_fields = ("taxonomy",)

	filter_horizontal = ("habitat",)
	readonly_fields = ["taxonomy"]
	fieldsets = (
		(None, {"fields": ["taxonomy"]}),
		("IUCN Status", {"fields": ("iucn_global", "iucn_europe", "iucn_mediterranean")}),
		("Other Information", {"fields": ("habitat",)}),
	)


admin.site.register(IUCNData, IUCNDataAdmin)


class SystemAdmin(admin.ModelAdmin):
	list_display = ("taxonomy", "freshwater", "marine", "terrestrial")
	list_filter = ("freshwater", "marine", "terrestrial")
	search_fields = ("taxonomy__name",)
	autocomplete_fields = ("taxonomy",)

	readonly_fields = ["taxonomy"]
	fieldsets = (
		(None, {"fields": ["taxonomy"]}),
		("System", {"fields": ("freshwater", "marine", "terrestrial")}),
	)


admin.site.register(System, SystemAdmin)


class TaxonTagAdmin(admin.ModelAdmin):
	list_display = ("taxonomy",)
	search_fields = ("taxonomy__name",)
	autocomplete_fields = ("taxonomy",)

	filter_horizontal = ("tags",)
	readonly_fields = ["taxonomy"]
	fieldsets = (
		(None, {"fields": ["taxonomy"]}),
		("Other Information", {"fields": ("tags",)}),
	)

	def formfield_for_manytomany(self, db_field, request, **kwargs):
		if db_field.name == "tags":
			kwargs["queryset"] = Tag.objects.all().order_by("name")
		return super().formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(TaxonTag, TaxonTagAdmin)


class DirectiveAdmin(admin.ModelAdmin):
	list_display = (
		"taxon_name",
		"taxonomy",
		"cites",
		"ceea",
		"lespre",
		"directiva_aves",
		"directiva_habitats",
	)
	list_filter = (
		"cites",
		"ceea",
		"lespre",
		"directiva_aves",
		"directiva_habitats",
	)
	search_fields = ("taxon_name", "taxon__name")
	autocomplete_fields = ("taxonomy",)

	readonly_fields = ["taxon_name", "taxonomy"]
	fieldsets = (
		(None, {"fields": ["taxon_name", "taxonomy"]}),
		(
			"Directivas",
			{
				"fields": (
					"cites",
					"ceea",
					"lespre",
					"directiva_aves",
					"directiva_habitats",
				)
			},
		),
	)


admin.site.register(Directive, DirectiveAdmin)
