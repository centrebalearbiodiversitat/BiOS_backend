import csv
import json

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_datetime

from apps.genetics.models import GeneticFeatures, Produces, Gene, Product
from apps.occurrences.models import Occurrence
from apps.taxonomy.models import TaxonomicLevel
from apps.versioning.models import Batch, Source


def parse_line(line: dict):
    for key, value in line.items():
        try:
            line[key] = json.loads(value)
        except:
            pass  # is not json format

    return line


class Command(BaseCommand):
    help = "Loads occurrences from csv"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        file_name = options['file']
        with open(file_name, encoding='utf-8') as file:
            csv_file = csv.DictReader(file)
            batch = Batch.objects.create()
            line: dict
            for line in csv_file:
                line = parse_line(line)
                print(line)
                source, _ = Source.objects.get_or_create(
                    name=line['geneticSource'],
                    defaults={
                        'accepted': True,
                        'origin': Source.TRANSLATE_CHOICES[line['geneticOrigin']]
                    }
                )
                batch.sources.add(source)

                gfs, _ = GeneticFeatures.objects.get_or_create(
                    sample_id=line['sample_id'],
                    defaults={
                        'isolate': line['isolate'],
                        'bp': line['bp'],
                        'definition': line['definition'],
                        'data_file_division': line['data_file_division'],
                        'published_date': parse_datetime(line['date']) if line['date'] else None,
                        'collection_date': parse_datetime(line['collection_date']) if line['collection_date'] else None,
                        'molecule_type': line['molecule_type'],
                        'sequence_version': line['sequence_version'],
                    }
                )

                gfs.references.add(batch)

                for production in line['genetic_features']:
                    gene = None
                    product = None
                    if production['gene']:
                        gene, _ = Gene.objects.get_or_create(name=production['gene'], accepted=True)
                        gene.references.add(batch)
                    if production['product']:
                        product, _ = Product.objects.get_or_create(name=production['product'], accepted=True)
                        product.references.add(batch)
                    prod_rel, _ = Produces.objects.get_or_create(
                        gene=gene,
                        product=product
                    )
                    prod_rel.references.add(batch)
                    gfs.products.add(prod_rel)

                taxonomy = TaxonomicLevel.objects.find(line['taxon'])

                assert taxonomy.count() == 1, f'Multiple taxonomy trees found for {line["taxon"]}'

                occ, _ = Occurrence.objects.get_or_create(
                    voucher=line['voucher'] or '',
                    defaults={
                        'locality': line['locality'] or '',
                        'latitude': line['lat_lon'][0] if line['lat_lon'] else '',
                        'longitude': line['lat_lon'][1] if line['lat_lon'] else '',
                        'collection_date': parse_datetime(line['collection_date']) if line['collection_date'] else None,
                        'taxonomy': taxonomy.first(),
                        'genetic_features': gfs
                    }
                )
                occ.references.add(batch)
