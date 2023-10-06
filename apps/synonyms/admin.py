from django.contrib import admin

from apps.synonyms.models import AuthorshipSynonym, KingdomSynonym, PhylumSynonym, ClassSynonym, OrderSynonym, \
	FamilySynonym, GenusSynonym, SpeciesSynonym, SubspeciesSynonym

admin.site.register(AuthorshipSynonym)
admin.site.register(KingdomSynonym)
admin.site.register(PhylumSynonym)
admin.site.register(ClassSynonym)
admin.site.register(OrderSynonym)
admin.site.register(FamilySynonym)
admin.site.register(GenusSynonym)
admin.site.register(SpeciesSynonym)
admin.site.register(SubspeciesSynonym)