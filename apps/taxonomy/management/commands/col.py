import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.synonyms.models import Synonym
from apps.taxonomy.models import Kingdom, Authorship, Phylum, Class, Order, Family, Genus, Species, Subspecies, \
    TaxonomicLevel
from apps.versioning.models import Batch, Source

KINGDOM, AUTH_KINGDOM, SOURCE_KINGDOM, SOURCE_ORIGIN_KINGDOM = 'Kingdom', 'kingdomAuthor', 'kingdomSource', 'kingdomOrigin'
PHYLUM, AUTH_PHYLUM, SOURCE_PHYLUM, SOURCE_ORIGIN_PHYLUM = 'Phylum', 'phylumAuthor', 'phylumSource', 'phylumOrigin'
CLASS, AUTH_CLASS, SOURCE_CLASS, SOURCE_ORIGIN_CLASS = 'Class', 'classAuthor', 'classSource', 'classOrigin'
ORDER, AUTH_ORDER, SOURCE_ORDER, SOURCE_ORIGIN_ORDER = 'Order', 'orderAuthor', 'orderSource', 'orderOrigin'
FAM, AUTH_FAM, SOURCE_FAM, SOURCE_ORIGIN_FAM = 'Family', 'familyAuthor', 'familySource', 'familyOrigin'
GENUS, AUTH_GENUS, SOURCE_GENUS, SOURCE_ORIGIN_GENUS = 'Genus', 'genusAuthor', 'genusSource', 'genusOrigin'
SPECIES, AUTH_SPECIES, SOURCE_SPECIES, SOURCE_ORIGIN_SPECIES = 'Species', 'speciesAuthor', 'speciesSource', 'speciesOrigin'
SUBSPECIES, AUTH_SUBSPECIES, SOURCE_SUBSPECIES, SOURCE_ORIGIN_SUBSPECIES = 'Subspecies', 'subspeciesAuthor', 'subspeciesSource', 'subspeciesOrigin'
TAXON_RANK = 'taxonRank'

LEVELS = [KINGDOM, PHYLUM, CLASS, ORDER, FAM, GENUS, SPECIES, SUBSPECIES]

LEVELS_PARAMS = {
    KINGDOM: [Kingdom, Synonym, AUTH_KINGDOM, SOURCE_KINGDOM, SOURCE_ORIGIN_KINGDOM],
    PHYLUM: [Phylum, Synonym, AUTH_PHYLUM, SOURCE_PHYLUM, SOURCE_ORIGIN_PHYLUM],
    CLASS: [Class, Synonym, AUTH_CLASS, SOURCE_CLASS, SOURCE_ORIGIN_CLASS],
    ORDER: [Order, Synonym, AUTH_ORDER, SOURCE_ORDER, SOURCE_ORIGIN_ORDER],
    FAM: [Family, Synonym, AUTH_FAM, SOURCE_FAM, SOURCE_ORIGIN_FAM],
    GENUS: [Genus, Synonym, AUTH_GENUS, SOURCE_GENUS, SOURCE_ORIGIN_GENUS],
    SPECIES: [Species, Synonym, AUTH_SPECIES, SOURCE_SPECIES, SOURCE_ORIGIN_SPECIES],
    SUBSPECIES: [Subspecies, Synonym, AUTH_SUBSPECIES, SOURCE_SUBSPECIES, SOURCE_ORIGIN_SUBSPECIES]
}


def create_tax_level(line, model, syn_model, batch: Batch, idx_name, parent, idx_author, idx_source, idx_source_origin):
    auth = None
    if line[idx_author]:
        auth_syn, _ = Synonym.objects.get_or_create(name=line[idx_author])

        auth, _ = Authorship.objects.get_or_create(accepted=auth_syn)
        auth.synonyms.add(auth_syn)
        auth.references.add(batch)

    taxon_syn, _ = syn_model.objects.get_or_create(name=line[idx_name] if line[idx_name] else 'Unknown')
    if parent:  # Kingdom does not have parent
        child, _ = model.objects.get_or_create(
            accepted=taxon_syn,
            parent=parent,
            defaults={
                'rank': TaxonomicLevel.TRANSLATE_RANK[idx_name.lower()],
                'authorship': auth,
            }
        )
    else:
        child, _ = model.objects.get_or_create(
            accepted=taxon_syn,
            defaults={
                'rank': TaxonomicLevel.TRANSLATE_RANK[idx_name.lower()],
                'authorship': auth,
            }
        )
    child.synonyms.add(taxon_syn)
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


@transaction.atomic
class Command(BaseCommand):
    help = "Loads from taxonomy from csv"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    def handle(self, *args, **options):
        file_name = options['file']
        with open(file_name, encoding='utf-8') as file:
            csv_file = csv.DictReader(file)
            batch = Batch.objects.create()
            line: dict
            for line in csv_file:
                # print(line)
                parent = None
                for level in LEVELS:
                    params = LEVELS_PARAMS[level]
                    print(line)
                    parent = create_tax_level(line, params[0], params[1], batch, level, parent, params[2], params[3], params[4])
                    if level.lower() == line[TAXON_RANK]:
                        break
