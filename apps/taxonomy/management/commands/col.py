import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import Kingdom, Authorship, Phylum, Class, Order, Family, Genus, Species, Subspecies
from apps.versioning.models import Batch, Source

KINGDOM, AUTH_KINGDOM, SOURCE_KINGDOM, SOURCE_ORIGIN_KINGDOM = range(0, 4)
PHYLUM, AUTH_PHYLUM, SOURCE_PHYLUM, SOURCE_ORIGIN_PHYLUM = range(4, 8)
CLASS, AUTH_CLASS, SOURCE_CLASS, SOURCE_ORIGIN_CLASS = range(8, 12)
ORDER, AUTH_ORDER, SOURCE_ORDER, SOURCE_ORIGIN_ORDER = range(12, 16)
FAM, AUTH_FAM, SOURCE_FAM, SOURCE_ORIGIN_FAM = range(16, 20)
GENUS, AUTH_GENUS, SOURCE_GENUS, SOURCE_ORIGIN_GENUS = range(20, 24)
SPECIES, AUTH_SPECIES, SOURCE_SPECIES, SOURCE_ORIGIN_SPECIES = range(24, 28)
SUBSPECIES, AUTH_SUBSPECIES, SOURCE_SUBSPECIES, SOURCE_ORIGIN_SUBSPECIES = range(28, 32)


def create_tax_level(line, model, batch: Batch, idx_name, parent_key, parent, idx_author, idx_source, idx_source_origin):
    auth, _ = Authorship.objects.update_or_create(line[idx_author])
    defaults = {
        'authorship': auth,
    }

    if parent_key:
        defaults[parent_key] = parent

    parent, _ = model.objects.update_or_create(
        name=line[idx_name],
        defaults=defaults
    )

    parent.references.add(batch)
    source, _ = Source.objects.update_or_create(
        name=line[idx_source],
        defaults={
            'origin': Source.TRANSLATE_CHOICES[line[idx_source_origin]]
        }
    )
    batch.sources.add(source)

    return parent


@transaction.atomic
class Command(BaseCommand):
    help = "Loads from taxonomy from csv"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    def handle(self, *args, **options):
        file_name = options['file']
        with open(file_name) as file:
            csv_file = csv.reader(file)
            batch = Batch.objects.create()
            next(csv_file)
            for line in csv_file:
                print(line)
                parent = create_tax_level(line, Kingdom, batch, KINGDOM, None, None, AUTH_KINGDOM, SOURCE_KINGDOM, SOURCE_ORIGIN_KINGDOM)
                parent = create_tax_level(line, Phylum, batch, PHYLUM, 'kingdom', parent, AUTH_PHYLUM, SOURCE_PHYLUM, SOURCE_ORIGIN_PHYLUM)
                parent = create_tax_level(line, Class, batch, CLASS, 'phylum', parent, AUTH_CLASS, SOURCE_CLASS, SOURCE_ORIGIN_CLASS)
                parent = create_tax_level(line, Order, batch, ORDER, 'classis', parent, AUTH_ORDER, SOURCE_ORDER, SOURCE_ORIGIN_ORDER)
                parent = create_tax_level(line, Family, batch, FAM, 'order', parent, AUTH_FAM, SOURCE_FAM, SOURCE_ORIGIN_FAM)
                parent = create_tax_level(line, Genus, batch, GENUS, 'family', parent, AUTH_FAM, SOURCE_FAM, SOURCE_ORIGIN_FAM)
                parent = create_tax_level(line, Species, batch, SPECIES, 'genus', parent, AUTH_SPECIES, SOURCE_SPECIES, SOURCE_ORIGIN_SPECIES)
                parent = create_tax_level(line, Subspecies, batch, SUBSPECIES, 'species', parent, AUTH_SUBSPECIES, SOURCE_SUBSPECIES, SOURCE_ORIGIN_SUBSPECIES)



