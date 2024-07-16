from django.contrib import admin

from apps.genetics.models import Gene, Sequence


class GeneAdmin(admin.ModelAdmin):
	search_fields = ["unidecode_name"]
	autocomplete_fields = ["synonyms", "sources"]


# class ProductAdmin(admin.ModelAdmin):
# 	search_fields = ["unidecode_name"]
# 	autocomplete_fields = ["synonyms", "sources"]


# class ProducesAdmin(admin.ModelAdmin):
# 	search_fields = ["gene", "product"]
# 	autocomplete_fields = ["gene", "product", "sources"]


class SequenceAdmin(admin.ModelAdmin):
	readonly_fields = ["occurrence"]
	autocomplete_fields = ["sources", 'genes']


admin.site.register(Gene, GeneAdmin)
# admin.site.register(Product, ProductAdmin)
# admin.site.register(Produces, ProducesAdmin)
admin.site.register(Sequence, SequenceAdmin)
