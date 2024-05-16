from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from apps.taxonomy.models import Authorship, TaxonomicLevel


class BaseTaxonLevelAdmin(MPTTModelAdmin):
	list_display = ['scientific_name', 'rank', 'upper_taxon', 'num_children', 'verbatim_authorship', 'parsed_year']  # , 'num_references'
	list_filter = ['rank', 'accepted']
	fields = ['name', 'verbatim_authorship', 'rank', 'parent', 'accepted', 'sources', 'synonyms', 'batch', 'parsed_year', 'authorship']
	search_fields = ['unidecode_name', 'verbatim_authorship']
	autocomplete_fields = ['parent', 'synonyms', 'authorship', 'sources']
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

	def num_references(self, obj):
		return obj.references.count()

	def num_children(self, obj):
		return obj.get_children().count()

	def upper_taxon(self, obj):
		full_taxon_str = ''
		upper_taxa = obj.get_ancestors(ascending=True)
		for taxon in upper_taxa:
			full_taxon_str = f'{full_taxon_str} < {taxon}'

		return full_taxon_str if len(full_taxon_str) < 3 else full_taxon_str[3:]


admin.site.register(TaxonomicLevel, BaseTaxonLevelAdmin)


class AuthorshipAdmin(admin.ModelAdmin):
	search_fields = ['unidecode_name']
	list_display = ['name']


admin.site.register(Authorship, AuthorshipAdmin)
