from django.db import models
from django.db.models import F

from apps.occurrences.models import Occurrence
from common.utils.models import ReferencedModel, SynonymModel


class Marker(ReferencedModel, SynonymModel):
	name = models.CharField(max_length=512, null=True, blank=True, default=None)
	product = models.CharField(max_length=512, null=True, blank=True, default=None)


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
		indexes = [
			models.Index(fields=["occurrence"]),
			models.Index(fields=["published_date"]),
		]
		ordering = [F("published_date").desc(nulls_last=True), "id"]
