from django.contrib import admin

from apps.genetics.models import Gene, GeneticFeatures, Produces, Product

admin.site.register(Gene)
admin.site.register(Product)
admin.site.register(Produces)
admin.site.register(GeneticFeatures)