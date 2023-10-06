from django.db import models

from apps.genetics.models import GeneticFeatures
from apps.versioning.models import ModelWithReferences


class Occurrence(ModelWithReferences):
    og_location = models.CharField(max_length=255)
    collection_date = models.DateField()
    genetic_features = models.ForeignKey(GeneticFeatures, on_delete=models.SET_NULL, null=True, blank=True)
