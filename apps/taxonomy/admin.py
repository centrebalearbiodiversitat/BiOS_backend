from django.contrib import admin

from apps.taxonomy.models import Authorship, TaxonomicLevel


class BaseTaxonLevelAdmin(admin.ModelAdmin):
	list_display = ['scientific_name', 'rank', 'upper_taxon', 'num_references', 'num_children', 'verbatim_authorship']
	list_filter = ['rank', 'accepted']
	fields = ['name', 'verbatim_authorship', 'rank', 'parent', 'accepted', 'synonyms', 'references', 'authorship', 'parsed_year']
	search_fields = ['unidecode_name', 'verbatim_authorship']
	autocomplete_fields = ['parent', 'synonyms']
	# exclude = ['references']

	def name(self, obj):
		return obj

	def sources(self, obj):
		map_sources = {}

		for batch in obj.references.all():
			for source in batch.sources.all():
				map_sources[source] = True

		return list(map_sources.keys())

	def num_references(self, obj):
		return obj.references.count()

	def num_children(self, obj):
		return obj.children.all().count()

	def upper_taxon(self, obj):
		taxon = ''
		current = obj
		while current.parent:
			taxon = f'{taxon} < {current.parent}'
			current = current.parent

		return taxon if len(taxon) < 3 else taxon[3:]


admin.site.register(TaxonomicLevel, BaseTaxonLevelAdmin)


class AuthorshipAdmin(admin.ModelAdmin):
	search_fields = ['unidecode_name']
	list_display = ['name']


admin.site.register(Authorship, AuthorshipAdmin)
