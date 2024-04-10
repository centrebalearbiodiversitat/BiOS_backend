import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import Authorship, TaxonomicLevel
from apps.versioning.models import Batch, Source

KINGDOM, AUTH_KINGDOM, SOURCE_KINGDOM, SOURCE_ORIGIN_KINGDOM = 'Kingdom', 'kingdomAuthor', 'kingdomSource', 'kingdomOrigin'
PHYLUM, AUTH_PHYLUM, SOURCE_PHYLUM, SOURCE_ORIGIN_PHYLUM = 'Phylum', 'phylumAuthor', 'phylumSource', 'phylumOrigin'
CLASS, AUTH_CLASS, SOURCE_CLASS, SOURCE_ORIGIN_CLASS = 'Class', 'classAuthor', 'classSource', 'classOrigin'
ORDER, AUTH_ORDER, SOURCE_ORDER, SOURCE_ORIGIN_ORDER = 'Order', 'orderAuthor', 'orderSource', 'orderOrigin'
FAM, AUTH_FAM, SOURCE_FAM, SOURCE_ORIGIN_FAM = 'Family', 'familyAuthor', 'familySource', 'familyOrigin'
GENUS, AUTH_GENUS, SOURCE_GENUS, SOURCE_ORIGIN_GENUS = 'Genus', 'genusAuthor', 'genusSource', 'genusOrigin'
SPECIES, AUTH_SPECIES, SOURCE_SPECIES, SOURCE_ORIGIN_SPECIES = 'Species', 'speciesAuthor', 'speciesSource', 'speciesOrigin'
SUBSPECIES, AUTH_SUBSPECIES, SOURCE_SUBSPECIES, SOURCE_ORIGIN_SUBSPECIES = 'Subspecies', 'subspeciesAuthor', 'subspeciesSource', 'subspeciesOrigin'
VARIETY, AUTH_VARIETY, SOURCE_VARIETY, SOURCE_ORIGIN_VARIETY = 'Variety', 'varietyAuthor', 'varietySource', 'varietyOrigin'
TAXON_RANK = 'taxonRank'

LEVELS = [KINGDOM, PHYLUM, CLASS, ORDER, FAM, GENUS, SPECIES, SUBSPECIES]
# LEVELS = [KINGDOM, PHYLUM, CLASS, ORDER, FAM, GENUS, SPECIES, SUBSPECIES, VARIETY]

LEVELS_PARAMS = {
    KINGDOM: [TaxonomicLevel.KINGDOM, AUTH_KINGDOM, SOURCE_KINGDOM, SOURCE_ORIGIN_KINGDOM],
    PHYLUM: [TaxonomicLevel.PHYLUM, AUTH_PHYLUM, SOURCE_PHYLUM, SOURCE_ORIGIN_PHYLUM],
    CLASS: [TaxonomicLevel.CLASS, AUTH_CLASS, SOURCE_CLASS, SOURCE_ORIGIN_CLASS],
    ORDER: [TaxonomicLevel.ORDER, AUTH_ORDER, SOURCE_ORDER, SOURCE_ORIGIN_ORDER],
    FAM: [TaxonomicLevel.FAMILY, AUTH_FAM, SOURCE_FAM, SOURCE_ORIGIN_FAM],
    GENUS: [TaxonomicLevel.GENUS, AUTH_GENUS, SOURCE_GENUS, SOURCE_ORIGIN_GENUS],
    SPECIES: [TaxonomicLevel.SPECIES, AUTH_SPECIES, SOURCE_SPECIES, SOURCE_ORIGIN_SPECIES],
    SUBSPECIES: [TaxonomicLevel.SUBSPECIES, AUTH_SUBSPECIES, SOURCE_SUBSPECIES, SOURCE_ORIGIN_SUBSPECIES],
    # VARIETY: [TaxonomicLevel.VARIETY, AUTH_VARIETY, SOURCE_VARIETY, SOURCE_ORIGIN_VARIETY]
}


def create_tax_level(line, parent, batch: Batch, idx_name, rank, idx_author, idx_source, idx_source_origin):
    if not line[idx_name]:  # Unknown level yet
        return parent

    auth = None
    if line[idx_author]:
        auth, _ = Authorship.objects.get_or_create(name=line[idx_author], accepted=True)
        auth.references.add(batch)

    child, _ = TaxonomicLevel.objects.get_or_create(
        parent=parent,
        name=line[idx_name],
        rank=rank,
        defaults={
            'accepted': True,
            'authorship': auth,
        }
    )
    child.references.add(batch)

    if not line[idx_source]:
        raise Exception('All records must have a source')

    source, _ = Source.objects.get_or_create(
        name=line[idx_source],
        defaults={
            'origin': Source.TRANSLATE_CHOICES[line[idx_source_origin]]
        }
    )
    batch.sources.add(source)

    return child


class Command(BaseCommand):
    help = "Loads from taxonomy from csv"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)
        parser.add_argument("-d", nargs='?', type=str, default=';')

    @transaction.atomic
    def handle(self, *args, **options):
        file_name = options['file']
        delimiter = options['d']
        with open(file_name, encoding='utf-8') as file:
            csv_file = csv.DictReader(file, delimiter=delimiter)
            batch = Batch.objects.create()
            line: dict
            for line in csv_file:
                print(line)
                parent = None
                for level in LEVELS:
                    params = LEVELS_PARAMS[level]
                    parent = create_tax_level(line, parent, batch, level, *params)
