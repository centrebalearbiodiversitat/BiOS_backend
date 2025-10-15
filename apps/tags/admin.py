from django.contrib import admin

from apps.tags.models import Habitat, TaxonTag, Tag, System, IUCNData, Directive, HabitatTaxonomy
from common.utils.admin import ReadOnlyBatch


class TagAdmin(admin.ModelAdmin):
	search_fields = ["name", "tag_type"]
	list_display = ["name", "tag_type"]
	fields = ["name", "tag_type"]


admin.site.register(Tag, TagAdmin)


class HabitatAdmin(ReadOnlyBatch):
	search_fields = ["name"]
	list_display = ["name"]
	fields = ["name", "sources"]
	readonly_fields = ["name"]
	autocomplete_fields = ["sources"]


admin.site.register(Habitat, HabitatAdmin)


class HabitatTaxonomyAdmin(ReadOnlyBatch):
	list_display = ("taxonomy", "habitat")
	list_filter = ("habitat",)
	search_fields = ("taxonomy__name",)
	autocomplete_fields = ("taxonomy", "sources")


admin.site.register(HabitatTaxonomy, HabitatTaxonomyAdmin)


class IUCNDataAdmin(ReadOnlyBatch):
	list_display = ("taxonomy", "assessment", "region")
	list_filter = ("assessment", "region")
	search_fields = ("taxonomy__name",)
	autocomplete_fields = ("taxonomy", "sources")


admin.site.register(IUCNData, IUCNDataAdmin)


class SystemAdmin(ReadOnlyBatch):
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


class TaxonTagAdmin(ReadOnlyBatch):
	list_display = ("taxonomy", "tag_name", "tag_type")
	search_fields = ("taxonomy__name",)
	autocomplete_fields = ("taxonomy", "sources")
	list_filter = ("tag__tag_type",)

	@admin.display(ordering="tag__name")
	def tag_name(self, obj):
		return obj.tag.name

	@admin.display(ordering="tag__tag_type")
	def tag_type(self, obj):
		return obj.tag.translate_tag_type()


admin.site.register(TaxonTag, TaxonTagAdmin)


class DirectiveAdmin(ReadOnlyBatch):
	list_display = (
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
	search_fields = ("taxonomy__name",)
	autocomplete_fields = ("taxonomy",)

	readonly_fields = ("taxonomy", )
	fieldsets = (
		(None, {"fields": ["taxonomy"]}),
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
