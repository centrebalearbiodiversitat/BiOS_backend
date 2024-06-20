from django.db import models
from apps.occurrences.models import Occurrence
from common.utils.models import ReferencedModel, SynonymModel


class Gene(ReferencedModel, SynonymModel):
	pass


class Product(ReferencedModel, SynonymModel):
	pass


class Produces(ReferencedModel):
	gene = models.ForeignKey(Gene, on_delete=models.PROTECT, null=True)
	product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)

	def __str__(self):
		return f"{self.gene} -> {self.product}"

	class Meta:
		verbose_name_plural = "Produces"


class Sequence(ReferencedModel):
	occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE)
	isolate = models.CharField(max_length=255, null=True, blank=True)
	bp = models.PositiveIntegerField()
	definition = models.TextField()
	data_file_division = models.CharField(max_length=255)
	published_date = models.DateField(blank=True, null=True)
	molecule_type = models.CharField(max_length=255)
	sequence_version = models.PositiveIntegerField()
	products = models.ManyToManyField(Produces)

	def __str__(self):
		return self.definition
