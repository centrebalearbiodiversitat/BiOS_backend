from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from apps.taxonomy.models import Authorship, Habitat, TaxonData, TaxonomicLevel


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
	list_display = ("taxonomy", "iucn_global", "iucn_europe", "iucn_mediterranean", "invasive")
	list_filter = ("iucn_global", "iucn_europe", "iucn_mediterranean", "invasive", "domesticated")
	search_fields = ("taxonomy__name",)
	filter_horizontal = ("habitat",)
	fieldsets = (
		("System", {"fields": ("freshwater", "marine", "terrestrial")}),
		("IUCN Status", {"fields": ("iucn_global", "iucn_europe", "iucn_mediterranean")}),
		("Other Information", {"fields": ("invasive", "domesticated", "habitat")}),
	)


admin.site.register(TaxonData, TaxonDataAdmin)


class HabitatAdmin(admin.ModelAdmin):
	search_fields = ["name"]
	list_display = ["name"]


admin.site.register(Habitat, HabitatAdmin)


class AuthorshipAdmin(admin.ModelAdmin):
	search_fields = ["unidecode_name"]
	list_display = ["name"]


admin.site.register(Authorship, AuthorshipAdmin)
