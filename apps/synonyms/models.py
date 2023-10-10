from django.db import models
from polymorphic.models import PolymorphicModel

# class TaxonIDs(models.Model):
# 	name = models.CharField(max_length=256, unique=True)


class Synonym(PolymorphicModel):
	name = models.CharField(max_length=256, unique=True)

	def clean(self):
		super().clean()
		self.name = self.name.strip()

	def __str__(self):
		return self.name

	class Meta:
		abstract = True


class AuthorshipSynonym(Synonym):
	pass


class KingdomSynonym(Synonym):
	pass


class PhylumSynonym(Synonym):
	pass


class ClassSynonym(Synonym):
	pass


class OrderSynonym(Synonym):
	pass


class FamilySynonym(Synonym):
	pass


class GenusSynonym(Synonym):
	pass


class SpeciesSynonym(Synonym):
	pass


class SubspeciesSynonym(Synonym):
	pass
