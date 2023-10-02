from django.contrib import admin

from apps.taxonomy.models import Authorship, Kingdom, Genus, Family, Species, Phylum, Order, Class, Subspecies

admin.site.register(Authorship)
admin.site.register(Kingdom)
admin.site.register(Genus)
admin.site.register(Family)
admin.site.register(Species)
admin.site.register(Subspecies)
admin.site.register(Phylum)
admin.site.register(Order)
admin.site.register(Class)
