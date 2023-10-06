from django.db import models

from apps.occurrences.models import Occurrence
from apps.synonyms.models import KingdomSynonym, PhylumSynonym, ClassSynonym, OrderSynonym, \
    FamilySynonym, AuthorshipSynonym, GenusSynonym, SpeciesSynonym, SubspeciesSynonym
from apps.versioning.models import ModelWithReferences


class Authorship(ModelWithReferences):
    synonyms = models.ManyToManyField(AuthorshipSynonym, related_name='+')
    accepted = models.ForeignKey(AuthorshipSynonym, on_delete=models.PROTECT, related_name='+')

    def __str__(self):
        return str(self.accepted)


class TaxonomicLevel(ModelWithReferences):
    capitalize = False
    authorship = models.ForeignKey(Authorship, on_delete=models.SET_NULL, null=True, default=None, blank=True)
    occurrences = models.ManyToManyField(Occurrence, blank=True)

    def __str__(self):
        if self.authorship:
            return f'{self.accepted} {self.authorship}'
        else:
            return str(self.accepted)

    def clean(self):
        super().clean()
        if self.capitalize:
            self.accepted.name = self.accepted.name.capitalize()
        else:
            self.accepted.name = self.accepted.name.lower()

        self.accepted.save()

    class MetaUnique:
        unique_together = ('parent', 'accepted')


class Kingdom(TaxonomicLevel):
    capitalize = True
    parent=None
    synonyms = models.ManyToManyField(KingdomSynonym, related_name='+')
    accepted = models.ForeignKey(KingdomSynonym, on_delete=models.PROTECT, related_name='+')

    class Meta:
        unique_together = ['accepted']
        verbose_name_plural = "1. Kingdoms"


class Phylum(TaxonomicLevel):
    synonyms = models.ManyToManyField(PhylumSynonym, related_name='+')
    accepted = models.ForeignKey(PhylumSynonym, on_delete=models.PROTECT, related_name='+')
    parent = models.ForeignKey(Kingdom, on_delete=models.SET_NULL, null=True, default=None, blank=True, related_name='children')

    class Meta(TaxonomicLevel.MetaUnique):
        verbose_name_plural = "2. Phyla"


class Class(TaxonomicLevel):
    synonyms = models.ManyToManyField(ClassSynonym, related_name='+')
    accepted = models.ForeignKey(ClassSynonym, on_delete=models.PROTECT, related_name='+')
    parent = models.ForeignKey(Phylum, on_delete=models.SET_NULL, null=True, default=None, blank=True, related_name='children')

    class Meta(TaxonomicLevel.MetaUnique):
        verbose_name_plural = "3. Classes"


class Order(TaxonomicLevel):
    synonyms = models.ManyToManyField(OrderSynonym, related_name='+')
    accepted = models.ForeignKey(OrderSynonym, on_delete=models.PROTECT, related_name='+')
    parent = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, default=None, blank=True, related_name='children')

    class Meta(TaxonomicLevel.MetaUnique):
        verbose_name_plural = "4. Orders"


class Family(TaxonomicLevel):
    synonyms = models.ManyToManyField(FamilySynonym, related_name='+')
    accepted = models.ForeignKey(FamilySynonym, on_delete=models.PROTECT, related_name='+')
    parent = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, default=None, blank=True, related_name='children')

    class Meta(TaxonomicLevel.MetaUnique):
        verbose_name_plural = "5. Families"


class Genus(TaxonomicLevel):
    capitalize = True
    synonyms = models.ManyToManyField(GenusSynonym, related_name='+')
    accepted = models.ForeignKey(GenusSynonym, on_delete=models.PROTECT, related_name='+')
    parent = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, default=None, blank=True, related_name='children')

    class Meta(TaxonomicLevel.MetaUnique):
        verbose_name_plural = "6. Genera"


class Species(TaxonomicLevel):
    synonyms = models.ManyToManyField(SpeciesSynonym, related_name='+')
    accepted = models.ForeignKey(SpeciesSynonym, on_delete=models.PROTECT, related_name='+')
    parent = models.ForeignKey(Genus, on_delete=models.SET_NULL, null=True, default=None, blank=True, related_name='children')

    class Meta(TaxonomicLevel.MetaUnique):
        verbose_name_plural = "7. Species"


class Subspecies(TaxonomicLevel):
    synonyms = models.ManyToManyField(SubspeciesSynonym, related_name='+')
    accepted = models.ForeignKey(SubspeciesSynonym, on_delete=models.PROTECT, related_name='+')
    parent = models.ForeignKey(Species, on_delete=models.SET_NULL, null=True, default=None, blank=True, related_name='children')

    class Meta(TaxonomicLevel.MetaUnique):
        verbose_name_plural = "8. Subspecies"
