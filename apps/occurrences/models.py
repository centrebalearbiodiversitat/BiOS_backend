from django.db import models

from apps.genetics.models import GeneticFeatures
from apps.taxonomy.models import TaxonomicLevel
from apps.versioning.models import ModelWithReferences


class Occurrence(ModelWithReferences):
    voucher = models.CharField(max_length=255)
    locality = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    collection_date = models.DateField(null=True, blank=True)
    genetic_features = models.ForeignKey(GeneticFeatures, on_delete=models.DO_NOTHING, null=True, blank=True)
    taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f'{self.taxonomy.binomial_scientific_name()} ({self.voucher})'
