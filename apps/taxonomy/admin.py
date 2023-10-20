from django.contrib import admin

from apps.taxonomy.models import Authorship, Kingdom, Genus, Family, Species, Phylum, Order, Class, Subspecies, \
	TaxonomicLevel, Variety
from common.admin import BaseSynonymAdmin


class BaseTaxonLevelAdmin(BaseSynonymAdmin):
	list_display = ['name', 'upper_taxon', 'num_references', 'num_children']

	def get_queryset(self, request):
		return super().get_queryset(request).filter(rank=self.model.RANK)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name in ["parent"]:
			kwargs["queryset"] = TaxonomicLevel.objects.filter(rank=self.model.PARENT)
		return super().formfield_for_foreignkey(db_field, request, **kwargs)

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


admin.site.register(Kingdom, BaseTaxonLevelAdmin)
admin.site.register(Phylum, BaseTaxonLevelAdmin)
admin.site.register(Genus, BaseTaxonLevelAdmin)
admin.site.register(Family, BaseTaxonLevelAdmin)
admin.site.register(Species, BaseTaxonLevelAdmin)
admin.site.register(Subspecies, BaseTaxonLevelAdmin)
admin.site.register(Order, BaseTaxonLevelAdmin)
admin.site.register(Class, BaseTaxonLevelAdmin)
admin.site.register(Variety, BaseTaxonLevelAdmin)

admin.site.register(Authorship)
