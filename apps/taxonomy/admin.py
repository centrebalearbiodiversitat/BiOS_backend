from django.contrib import admin

from apps.taxonomy.models import Authorship, Kingdom, Genus, Family, Species, Phylum, Order, Class, Subspecies, TaxonomicLevel


class BaseTaxonLevelAdmin(admin.ModelAdmin):
	list_display = ['name', 'sources', 'num_references', 'num_children']

	def get_queryset(self, request):
		return super().get_queryset(request).filter(rank=self.model.RANK)

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


admin.site.register(Kingdom, BaseTaxonLevelAdmin)


class TaxonLevelAdmin(BaseTaxonLevelAdmin):
	list_display = ['name', 'upper_taxon', 'sources', 'num_references']

	def upper_taxon(self, obj):
		taxon = ''
		current = obj
		while current.parent:
			taxon = f'{taxon} < {current.parent}'
			current = current.parent

		return taxon if len(taxon) < 3 else taxon[3:]


admin.site.register(Phylum, TaxonLevelAdmin)
admin.site.register(Genus, TaxonLevelAdmin)
admin.site.register(Family, TaxonLevelAdmin)
admin.site.register(Species, TaxonLevelAdmin)
admin.site.register(Subspecies, TaxonLevelAdmin)
admin.site.register(Order, TaxonLevelAdmin)
admin.site.register(Class, TaxonLevelAdmin)

admin.site.register(Authorship)
