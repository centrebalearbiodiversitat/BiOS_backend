from polymorphic.models import PolymorphicModel

from django.db import models

from common import utils


class Synonym(PolymorphicModel):
	KINGDOM = 0
	PHYLUM = 1
	CLASS = 2
	ORDER = 3
	FAMILY = 4
	GENUS = 5
	SPECIES = 6
	SUBSPECIES = 7
	GENE = 8
	PRODUCT = 9
	AUTHORSHIP = 10
	VARIETY = 11

	SYN_TYPES = (
		(KINGDOM, 'Kingdom'),
		(PHYLUM, 'Phylum'),
		(CLASS, 'Class'),
		(ORDER, 'Order'),
		(FAMILY, 'Family'),
		(GENUS, 'Genus'),
		(SPECIES, 'Species'),
		(SUBSPECIES, 'Subspecies'),
		(GENE, 'Gene'),
		(PRODUCT, 'Product'),
		(AUTHORSHIP, 'Authorship'),
		(VARIETY, 'Variety'),
	)

	name = models.CharField(max_length=256)
	type_of = models.PositiveSmallIntegerField(choices=SYN_TYPES)

	def clean(self):
		super().clean()
		self.name = utils.compact(self.name)

	def __str__(self):
		return self.name

	class Meta:
		indexes = []
		unique_together = ('name', 'type_of')


class ModelWithSynonyms(models.Model):
	SYNONYM_TYPE_OF = None
	synonyms = models.ManyToManyField(Synonym, related_name='+')
	accepted = models.ForeignKey(Synonym, on_delete=models.PROTECT, related_name='+')

	def __str__(self):
		return str(self.accepted)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		super().save(force_insert, force_update, using, update_fields)
		self.synonyms.add(self.accepted)

	class Meta:
		abstract = True
