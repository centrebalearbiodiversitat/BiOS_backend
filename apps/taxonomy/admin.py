from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from apps.taxonomy.models import Authorship, Habitat, TaxonData, TaxonomicLevel, Tag


class BaseTaxonLevelAdmin(MPTTModelAdmin):
	list_display = [
		"scientific_name",
		"rank",
		"upper_taxon",
		"verbatim_authorship",
		"parsed_year",
	]  # , 'num_references'
	list_filter = ["rank", "accepted"]
	fields = [
		"name",
		"verbatim_authorship",
		"rank",
		"parent",
		"accepted",
		"accepted_modifier",
		"sources",
		"synonyms",
		"batch",
		"parsed_year",
		"authorship",
	]
	search_fields = ["unidecode_name", "verbatim_authorship"]
	autocomplete_fields = ["parent", "synonyms", "authorship", "sources"]
	# exclude = ['references']
	mptt_indent_field = 1

	def name(self, obj):
		return obj

	# def sources(self, obj):
	# 	map_sources = {}
	#
	# 	for batch in obj.references.all():
	# 		for source in batch.sources.all():
	# 			map_sources[source] = True
	#
	# 	return list(map_sources.keys())

	def upper_taxon(self, obj):
		full_taxon_str = ""
		upper_taxa = obj.get_ancestors(ascending=True).exclude(rank=TaxonomicLevel.LIFE)
		for taxon in upper_taxa:
			full_taxon_str = f"{full_taxon_str} < {taxon}"

		return full_taxon_str if len(full_taxon_str) < 3 else full_taxon_str[3:]


admin.site.register(TaxonomicLevel, BaseTaxonLevelAdmin)


class TaxonDataAdmin(admin.ModelAdmin):
	list_display = ("taxonomy", "iucn_global", "iucn_europe", "iucn_mediterranean")
	list_filter = ("iucn_global", "iucn_europe", "iucn_mediterranean")
	search_fields = ("taxonomy__name",)
	autocomplete_fields = ()

	filter_horizontal = ("habitat", "tags")
	readonly_fields = ["taxonomy"]
	fieldsets = (
		(
			None,
			{
				"fields": [
					"taxonomy",
				]
			},
		),
		("System", {"fields": ("freshwater", "marine", "terrestrial")}),
		("IUCN Status", {"fields": ("iucn_global", "iucn_europe", "iucn_mediterranean")}),
		("Other Information", {"fields": ("habitat", "tags")}),
		
	)

	def formfield_for_manytomany(self, db_field, request, **kwargs):
		if db_field.name == "tags":
			kwargs["queryset"] = Tag.objects.all().order_by('name')
		return super().formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(TaxonData, TaxonDataAdmin)


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


class AuthorshipAdmin(admin.ModelAdmin):
	search_fields = ["unidecode_name"]
	list_display = ["name"]


admin.site.register(Authorship, AuthorshipAdmin)
