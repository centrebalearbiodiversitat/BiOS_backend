from django.db import models

from apps.geography.models import GeographicLevel
from apps.taxonomy.models import TaxonomicLevel
from common.utils.models import LatLonModel, ReferencedModel


class Occurrence(ReferencedModel, LatLonModel):
    LIVING = 0
    PRESERVED = 1
    FOSSIL = 2
    CITATION = 3
    HUMAN_OBSERVATION = 4
    MACHINE_OBSERVATION = 5
    UNKNOWN = 6

    BASIS_OF_RECORD = (
        (LIVING, 'Living'),
        (PRESERVED, 'Preserved'),
        (FOSSIL, 'Fossil'),
        (CITATION, 'Citation'),
        (HUMAN_OBSERVATION, 'Human observation'),
        (MACHINE_OBSERVATION, 'Machine observation'),
        (UNKNOWN, 'Unknown'),
    )

    TRANSLATE_BASIS_OF_RECORD = {
        LIVING: 'living',
        'living': LIVING,
        PRESERVED: 'preserved',
        'preserved': PRESERVED,
        FOSSIL: 'fossil',
        'fossil': FOSSIL,
        CITATION: 'citation',
        'citation': CITATION,
        HUMAN_OBSERVATION: 'human_observation',
        'human_observation': HUMAN_OBSERVATION,
        MACHINE_OBSERVATION: 'machine_observation',
        'machine_observation': MACHINE_OBSERVATION,
        UNKNOWN: 'unknown',
        'unknown': UNKNOWN,
    }

    taxonomy = models.ForeignKey(TaxonomicLevel, on_delete=models.CASCADE)
    voucher = models.CharField(max_length=255, null=True, blank=True)
    geographical_location = models.ForeignKey(GeographicLevel, on_delete=models.PROTECT, null=True, blank=True)
    collection_date = models.DateField(null=True, blank=True)
    basis_of_record = models.PositiveSmallIntegerField(choices=BASIS_OF_RECORD)

    def __str__(self):
        return f'{self.taxonomy} ({self.voucher})'
