from django.db import models

from apps.genetics.models import GeneticFeatures
from apps.geography.models import GeographicLevel
from apps.taxonomy.models import TaxonomicLevel
from apps.versioning.models import ModelWithReferences


class Occurrence(ModelWithReferences):
    voucher = models.CharField(max_length=255)
    geographical_location = models.ForeignKey(GeographicLevel, on_delete=models.PROTECT, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    collection_date = models.DateField(null=True, blank=True)
    genetic_features = models.ForeignKey(GeneticFeatures, on_delete=models.SET_NULL, null=True, blank=True)
    taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f'{self.taxonomy} ({self.voucher})'
