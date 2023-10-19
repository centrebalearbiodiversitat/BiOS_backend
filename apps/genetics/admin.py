from django.contrib import admin

from apps.genetics.models import Gene, GeneticFeatures, Produces, Product
from common.admin import BaseSynonymAdmin

admin.site.register(Gene, BaseSynonymAdmin)
admin.site.register(Product, BaseSynonymAdmin)
admin.site.register(Produces)
admin.site.register(GeneticFeatures)