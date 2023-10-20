from django.core.exceptions import ValidationError
from django.db import models

from apps.synonyms.models import ModelWithSynonyms, Synonym
from apps.versioning.models import ModelWithReferences


class Authorship(ModelWithReferences, ModelWithSynonyms):
    SYNONYM_TYPE_OF = Synonym.AUTHORSHIP


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

    KINGDOM = Synonym.KINGDOM
    PHYLUM = Synonym.PHYLUM
    CLASS = Synonym.CLASS
    ORDER = Synonym.ORDER
    FAMILY = Synonym.FAMILY
    GENUS = Synonym.GENUS
    SPECIES = Synonym.SPECIES
    SUBSPECIES = Synonym.SUBSPECIES
    VARIETY = Synonym.VARIETY

    RANK_CHOICES = (
        (KINGDOM, 'Kingdom'),
        (PHYLUM, 'Phylum'),
        (CLASS, 'Class'),
        (ORDER, 'Order'),
        (FAMILY, 'Family'),
        (GENUS, 'Genus'),
        (SPECIES, 'Species'),
        (SUBSPECIES, 'Subspecies'),
        (VARIETY, 'Variety'),
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
        VARIETY: False,
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
        VARIETY: 'variety',
        'variety': VARIETY,
    }

    rank = models.PositiveSmallIntegerField(choices=RANK_CHOICES)
    authorship = models.ForeignKey(Authorship, on_delete=models.SET_NULL, null=True, default=None, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, default=None, blank=True, related_name='children')

    def __str__(self):
        name = super().__str__()

        if self.rank > TaxonomicLevel.GENUS:
            return self.binomial_scientific_name()
        elif self.authorship:
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
        if self.authorship:
            full_name = f'{full_name} {self.authorship}'
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
    SYNONYM_TYPE_OF = RANK = TaxonomicLevel.KINGDOM
    PARENT = None

    class Meta:
        proxy = True
        verbose_name_plural = "1. Kingdoms"


class Phylum(TaxonomicLevel):
    SYNONYM_TYPE_OF = RANK = TaxonomicLevel.PHYLUM
    PARENT = TaxonomicLevel.KINGDOM

    class Meta:
        proxy = True
        verbose_name_plural = "2. Phyla"


class Class(TaxonomicLevel):
    SYNONYM_TYPE_OF = RANK = TaxonomicLevel.CLASS
    PARENT = TaxonomicLevel.PHYLUM

    class Meta:
        proxy = True
        verbose_name_plural = "3. Classes"


class Order(TaxonomicLevel):
    SYNONYM_TYPE_OF = RANK = TaxonomicLevel.ORDER
    PARENT = TaxonomicLevel.CLASS

    class Meta:
        proxy = True
        verbose_name_plural = "4. Orders"


class Family(TaxonomicLevel):
    SYNONYM_TYPE_OF = RANK = TaxonomicLevel.FAMILY
    PARENT = TaxonomicLevel.ORDER

    class Meta:
        proxy = True
        verbose_name_plural = "5. Families"


class Genus(TaxonomicLevel):
    SYNONYM_TYPE_OF = RANK = TaxonomicLevel.GENUS
    PARENT = TaxonomicLevel.FAMILY

    class Meta:
        proxy = True
        verbose_name_plural = "6. Genera"


class Species(TaxonomicLevel):
    SYNONYM_TYPE_OF = RANK = TaxonomicLevel.SPECIES
    PARENT = TaxonomicLevel.GENUS

    class Meta:
        proxy = True
        verbose_name_plural = "7. Species"


class Subspecies(TaxonomicLevel):
    SYNONYM_TYPE_OF = RANK = TaxonomicLevel.SUBSPECIES
    PARENT = TaxonomicLevel.SPECIES

    class Meta:
        proxy = True
        verbose_name_plural = "8. Subspecies"


class Variety(TaxonomicLevel):
    SYNONYM_TYPE_OF = RANK = TaxonomicLevel.VARIETY
    PARENT = TaxonomicLevel.SPECIES

    class Meta:
        proxy = True
        verbose_name_plural = "8. Varieties"
