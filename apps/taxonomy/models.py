from django.core.exceptions import ValidationError
from django.db import models

from common.utils.models import ReferencedModel, SynonymModel, SynonymManager
from common.utils.utils import str_clean_up


class Authorship(ReferencedModel, SynonymModel):
    pass


class TaxonomicLevelManager(SynonymManager):
    def get_queryset(self):
        return super().get_queryset().select_related('parent')

    def find(self, taxon):
        levels: list = taxon.split()
        assert len(levels) > 0, []

        query = self.filter(name__iexact=levels[0])
        for level in levels[1:]:
            query = self.filter(parent__in=query, name__iexact=level)

        return query

    def contains(self, taxon):
        levels: list = taxon.split()
        assert len(levels) > 0, []

        query = self.none()
        for level in levels:
            query |= self.filter(name__icontains=level)

        return query


class TaxonomicLevel(ReferencedModel, SynonymModel):
    objects = TaxonomicLevelManager()

    KINGDOM = 0
    PHYLUM = 1
    CLASS = 2
    ORDER = 3
    FAMILY = 4
    GENUS = 5
    SPECIES = 6
    SUBSPECIES = 7
    VARIETY = 8
    LIFE = 9

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
        (LIFE, 'Life'),
    )
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
        LIFE: 'life',
        'life': LIFE,
    }

    rank = models.PositiveSmallIntegerField(choices=RANK_CHOICES)
    verbatim_authorship = models.CharField(max_length=256, null=True, default=None, blank=True)
    parsed_year = models.PositiveIntegerField(null=True, default=None, blank=True)
    authorship = models.ForeignKey(Authorship, on_delete=models.SET_NULL, null=True, default=None, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None, blank=True, related_name='children')

    def clean(self):
        if self.verbatim_authorship:
            self.verbatim_authorship = str_clean_up(self.verbatim_authorship)
        return super().clean()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.rank == TaxonomicLevel.SPECIES and len(self.name.split()) != 1:
            raise ValidationError('Species level must be epithet separated of genus.')

        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.scientific_name()

    def readable_rank(self):
        return TaxonomicLevel.TRANSLATE_RANK[self.rank]

    def scientific_name(self):
        current = self
        full_name = super().__str__()
        while current.parent and current.rank in [TaxonomicLevel.SPECIES, TaxonomicLevel.SUBSPECIES, TaxonomicLevel.VARIETY]:
            full_name = f'{current.parent.name} {full_name}'
            current = current.parent
        # if self.authorship:
        #     full_name = f'{full_name} {self.authorship}'
        return full_name

    # def clean(self):
    #     super().clean()
        # if not ((not self.parent and isinstance(self, Kingdom)) or (self.parent and isinstance(self.parent, self.PARENT))):
        #     raise ValidationError('Parent taxonomic level error')

        # if TaxonomicLevel.RANK_CAPITALIZE[self.RANK]:
        #     self.accepted.name = self.accepted.name.capitalize()
        # else:
        #     self.accepted.name = self.accepted.name.lower()

        # self.accepted.save()

    class Meta:
        unique_together = ('parent', 'name', 'rank')
        # indexes = [
        #     models.Index(fields=['rank'], name='rank_idx'),
        # ]

