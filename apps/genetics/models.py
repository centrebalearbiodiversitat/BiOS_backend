from django.db import models
from django.db.models import F

from apps.occurrences.models import Occurrence
from common.utils.models import ReferencedModel, SynonymModel


class Product(models.Model):
	name = models.CharField(max_length=512, null=True, blank=True, default=None)

	def __str__(self):
		return self.name


class Marker(ReferencedModel, SynonymModel):
	products = models.ManyToManyField(Product, blank=True, symmetrical=False)


class Sequence(ReferencedModel):
	occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE)
	isolate = models.CharField(max_length=255, null=True, blank=True)
	definition = models.TextField(null=True, blank=True)
	published_date = models.DateField(blank=True, null=True)
	markers = models.ManyToManyField(Marker)

	def __str__(self):
		if self.definition:
			return f"{self.definition}"
		else:
			return f"{self.occurrence}"

	class Meta:
		ordering = [F("published_date").desc(nulls_last=True), "id"]
