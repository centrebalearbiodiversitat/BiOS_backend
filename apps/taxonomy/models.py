from django.core.exceptions import ValidationError
from django.db import models

from apps.synonyms.models import Synonym, ModelWithSynonyms
from apps.versioning.models import ModelWithReferences


class Authorship(ModelWithReferences, ModelWithSynonyms):
    pass


class TaxonomicLevelManager(models.Manager):
    def find(self, taxon):
        levels: list = taxon.split()
        assert len(levels) > 0, f'Invalid taxon string'
        query = self.filter(synonyms__name=levels[0])
        for level in levels[1:]:
            query = self.filter(parent__in=query, synonyms__name=level)

        return query


class TaxonomicLevel(ModelWithReferences, ModelWithSynonyms):
    objects = TaxonomicLevelManager()

    KINGDOM = 0
    PHYLUM = 1
    CLASS = 2
    ORDER = 3
    FAMILY = 4
    GENUS = 5
    SPECIES = 6
    SUBSPECIES = 7

    RANK_CHOICES = (
        (KINGDOM, 'Kingdom'),
        (PHYLUM, 'Phylum'),
        (CLASS, 'Class'),
        (ORDER, 'Order'),
        (FAMILY, 'Family'),
        (GENUS, 'Genus'),
        (SPECIES, 'Species'),
        (SUBSPECIES, 'Subspecies'),
    )
    RANK_CAPITALIZE = {
        KINGDOM: True,
        PHYLUM: True,
        CLASS: True,
        ORDER: True,
        FAMILY: True,
        GENUS: True,
        SPECIES: False,
        SUBSPECIES: False,
    }
    TRANSLATE_RANK = {
        KINGDOM: 'kingdom',
        'kingdom': KINGDOM,
        PHYLUM: 'phylum',
        'phylum': PHYLUM,
        CLASS: 'class',
        'class': CLASS,
        ORDER: 'order',
        'order': ORDER,
        FAMILY: 'family',
        'family': FAMILY,
        GENUS: 'genus',
        'genus': GENUS,
        SPECIES: 'species',
        'species': SPECIES,
        SUBSPECIES: 'subspecies',
        'subspecies': SUBSPECIES,
    }

    capitalize = False

    rank = models.PositiveSmallIntegerField(choices=RANK_CHOICES)
    authorship = models.ForeignKey(Authorship, on_delete=models.SET_NULL, null=True, default=None, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, default=None, blank=True, related_name='children')

    def __str__(self):
        name = super().__str__()

        if self.authorship:
            name = f'{name} {self.authorship}'

        return name

    def simple_name(self):
        return super().__str__()

    def binomial_scientific_name(self):
        current = self
        full_name = self.simple_name()
        while current.parent and current.rank > TaxonomicLevel.GENUS:
            full_name = f'{current.parent.simple_name()} {full_name}'
            current = current.parent

        return full_name

    def clean(self):
        super().clean()
        if not (self.rank == TaxonomicLevel.KINGDOM and self.parent == None or
                self.parent and self.rank == self.parent.rank + 1):
            raise ValidationError('Parent taxonomic level error')

        if TaxonomicLevel.RANK_CAPITALIZE[self.rank]:
            self.accepted.name = self.accepted.name.capitalize()
        else:
            self.accepted.name = self.accepted.name.lower()

        self.accepted.save()

    class Meta:
        unique_together = ('parent', 'accepted')
        indexes = [
            models.Index(fields=['rank'], name='rank_idx'),
        ]


class Kingdom(TaxonomicLevel):
    capitalize = True
    RANK = TaxonomicLevel.KINGDOM

    class Meta:
        proxy = True
        verbose_name_plural = "1. Kingdoms"


class Phylum(TaxonomicLevel):
    RANK = TaxonomicLevel.PHYLUM

    class Meta:
        proxy = True
        verbose_name_plural = "2. Phyla"


class Class(TaxonomicLevel):
    RANK = TaxonomicLevel.CLASS

    class Meta:
        proxy = True
        verbose_name_plural = "3. Classes"


class Order(TaxonomicLevel):
    RANK = TaxonomicLevel.ORDER

    class Meta:
        proxy = True
        verbose_name_plural = "4. Orders"


class Family(TaxonomicLevel):
    RANK = TaxonomicLevel.FAMILY

    class Meta:
        proxy = True
        verbose_name_plural = "5. Families"


class Genus(TaxonomicLevel):
    RANK = TaxonomicLevel.GENUS
    capitalize = True

    class Meta:
        proxy = True
        verbose_name_plural = "6. Genera"


class Species(TaxonomicLevel):
    RANK = TaxonomicLevel.SPECIES

    class Meta:
        proxy = True
        verbose_name_plural = "7. Species"


class Subspecies(TaxonomicLevel):
    RANK = TaxonomicLevel.SUBSPECIES

    class Meta:
        proxy = True
        verbose_name_plural = "8. Subspecies"
