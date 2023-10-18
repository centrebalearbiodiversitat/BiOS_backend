from django.core.exceptions import ValidationError
from django.db import models

from common import utils


class Synonym(models.Model):
	name = models.CharField(max_length=256, unique=True)

	def clean(self):
		super().clean()
		self.name = utils.compact(self.name)

	def __str__(self):
		return self.name

	class Meta:
		indexes = []


class ThirdPartyID(models.Model):
	taxon_id = models.CharField(max_length=256, unique=True)
	synonym = models.ForeignKey(Synonym, on_delete=models.CASCADE)

	def clean(self):
		super().clean()
		self.taxon_id = utils.compact(self.taxon_id)


class ModelWithSynonyms(models.Model):
	synonyms = models.ManyToManyField(Synonym, related_name='+')
	accepted = models.ForeignKey(Synonym, on_delete=models.PROTECT, related_name='+')

	def __str__(self):
		return str(self.accepted)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		super().save(force_insert, force_update, using, update_fields)
		self.synonyms.add(self.accepted)

	class Meta:
		abstract = True
