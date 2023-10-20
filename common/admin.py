from django.contrib import admin

from apps.synonyms.models import Synonym


class BaseSynonymAdmin(admin.ModelAdmin):
	def formfield_for_manytomany(self, db_field, request, **kwargs):
		if db_field.name == 'synonyms':
			kwargs["queryset"] = Synonym.objects.filter(type_of=self.model.SYNONYM_TYPE_OF)
		return super().formfield_for_manytomany(db_field, request, **kwargs)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name in ["accepted"]:
			kwargs["queryset"] = Synonym.objects.filter(type_of=self.model.SYNONYM_TYPE_OF)
		return super().formfield_for_foreignkey(db_field, request, **kwargs)
