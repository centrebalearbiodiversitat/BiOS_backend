from django.db import models
from apps.occurrences.models import Occurrence
from common.utils.models import ReferencedModel, SynonymModel


class Marker(ReferencedModel, SynonymModel):
	product = models.CharField(max_length=512, null=True, blank=True, default=None, db_index=True)


class Sequence(ReferencedModel):
	occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE)
	isolate = models.CharField(max_length=255, null=True, blank=True)
	bp = models.PositiveIntegerField()
	definition = models.TextField()
	data_file_division = models.CharField(max_length=255)
	published_date = models.DateField(blank=True, null=True)
	molecule_type = models.CharField(max_length=255)
	sequence_version = models.PositiveIntegerField()
	markers = models.ManyToManyField(Marker)

	def __str__(self):
		return self.definition
