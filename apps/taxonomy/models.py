from django.db import models

from apps.occurrences.models import Occurrence
from apps.versioning.models import ModelWithReferences


class Authorship(ModelWithReferences):
    name = models.CharField(max_length=256, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# class Synonym(ModelWithReferences):
#     name = models.CharField(max_length=256, unique=True)


class TaxonomicLevel(ModelWithReferences):
    capitalize = False
    name = models.CharField(max_length=256, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    authorship = models.ForeignKey(Authorship, on_delete=models.SET_NULL, null=True, default=None, blank=True)
    occurrences = models.ManyToManyField(Occurrence, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.capitalize:
            self.name = self.name.capitalize()
        else:
            self.name = self.name.lower()

    class Meta:
        abstract = True


class Kingdom(TaxonomicLevel):
    capitalize = True


class Phylum(TaxonomicLevel):
    kingdom = models.ForeignKey(Kingdom, on_delete=models.SET_NULL, null=True, default=None, blank=True)

    class Meta:
        verbose_name_plural = "phyla"


class Class(TaxonomicLevel):
    phylum = models.ForeignKey(Phylum, on_delete=models.SET_NULL, null=True, default=None, blank=True)

    class Meta:
        verbose_name_plural = "classes"


class Order(TaxonomicLevel):
    classis = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, default=None, blank=True)


class Family(TaxonomicLevel):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, default=None, blank=True)

    class Meta:
        verbose_name_plural = "families"


class Genus(TaxonomicLevel):
    capitalize = True
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, default=None, blank=True)

    class Meta:
        verbose_name_plural = "genera"


class Species(TaxonomicLevel):
    genus = models.ForeignKey(Genus, on_delete=models.SET_NULL, null=True, default=None, blank=True)

    class Meta:
        verbose_name_plural = "species"


class Subspecies(TaxonomicLevel):
    species = models.ForeignKey(Species, on_delete=models.SET_NULL, null=True, default=None, blank=True)

    class Meta:
        verbose_name_plural = "subspecies"
