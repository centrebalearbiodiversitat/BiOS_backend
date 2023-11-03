from django.contrib import admin

from apps.taxonomy.models import Authorship, TaxonomicLevel


class BaseTaxonLevelAdmin(admin.ModelAdmin):
	list_display = ['scientific_name', 'rank', 'upper_taxon', 'num_references', 'num_children']
	list_filter = ['rank']
	fields = ['name', 'rank', 'authorship', 'parent', 'accepted', 'synonyms', 'references', ]
	search_fields = ['name']
	autocomplete_fields = ['parent', 'authorship', 'synonyms']

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		# if db_field.name in ["parent"]:
		# 	print(self.model.rank)
		# 	if hasattr(self.model, 'PARENT'):
		# 		if self.model.PARENT:
		# 			kwargs["queryset"] = TaxonomicLevel.objects.filter(rank=self.model.PARENT)
		# 		else:
		# 			kwargs["queryset"] = TaxonomicLevel.objects.none()
		# 	else:
		# 		kwargs["queryset"] = TaxonomicLevel.objects.all()

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


admin.site.register(TaxonomicLevel, BaseTaxonLevelAdmin)


class AuthorshipAdmin(admin.ModelAdmin):
	search_fields = ['name']


admin.site.register(Authorship, AuthorshipAdmin)
