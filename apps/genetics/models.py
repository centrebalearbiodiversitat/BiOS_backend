from django.db import models

from apps.synonyms.models import ModelWithSynonyms
from apps.versioning.models import ModelWithReferences


class Gene(ModelWithReferences, ModelWithSynonyms):
    pass


class Product(ModelWithReferences, ModelWithSynonyms):
    pass


class Produces(ModelWithReferences):
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.gene} -> {self.product}'

    class Meta:
        verbose_name_plural = 'Produces'


class GeneticFeatures(ModelWithReferences):
    sample_id = models.CharField(max_length=255)
    isolate = models.CharField(max_length=255)
    bp = models.PositiveIntegerField()
    definition = models.TextField()
    voucher = models.CharField(max_length=255)
    data_file_division = models.CharField(max_length=255)
    published_date = models.DateField()
    collection_date = models.DateField()
    molecule_type = models.CharField(max_length=255)
    sequence_version = models.PositiveIntegerField()
    products = models.ManyToManyField(Produces)

    class Meta:
        verbose_name_plural = 'Genetic Features'
