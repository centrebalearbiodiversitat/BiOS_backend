from django.contrib import admin

from apps.genetics.models import Gene, GeneticFeatures, Produces, Product


class GeneAdmin(admin.ModelAdmin):
	search_fields = ["c"]
	autocomplete_fields = ["synonyms"]


class ProductAdmin(admin.ModelAdmin):
	search_fields = ["unidecode_name"]
	autocomplete_fields = ["synonyms"]


class ProducesAdmin(admin.ModelAdmin):
	search_fields = ["gene", "product"]
	autocomplete_fields = ["gene", "product"]


class GeneticFeaturesAdmin(admin.ModelAdmin):
	autocomplete_fields = ["products"]


admin.site.register(Gene, GeneAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Produces, ProducesAdmin)
admin.site.register(GeneticFeatures, GeneticFeaturesAdmin)
