from django.db import models

from apps.versioning.models import ModelWithReferences


class Gene(ModelWithReferences):
    name = models.CharField(max_length=255)


class Product(ModelWithReferences):
    name = models.CharField(max_length=255)


class Produces(ModelWithReferences):
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class GeneticFeatures(ModelWithReferences):
    sample_id = models.CharField(max_length=255)
    isolate = models.CharField(max_length=255)
    bp = models.PositiveIntegerField()
    definition = models.TextField()
    voucher = models.CharField(max_length=255)
    data_file_division = models.CharField(max_length=255)
    date = models.DateField()
    molecule_type = models.CharField(max_length=255)
    sequence_version = models.PositiveIntegerField()


class GenInGeneticFeature(ModelWithReferences):
    genetic_features = models.ForeignKey(GeneticFeatures, on_delete=models.CASCADE)
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)


class ProductInGeneticFeature(ModelWithReferences):
    genetic_features = models.ForeignKey(GeneticFeatures, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
