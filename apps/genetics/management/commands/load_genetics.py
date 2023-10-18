import csv
import json

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_datetime

from apps.genetics.models import GeneticFeatures, Produces, Gene, Product
from apps.occurrences.models import Occurrence
from apps.synonyms.models import Synonym
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
    help = "Loads from taxonomy from csv"

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
                        'origin': Source.TRANSLATE_CHOICES[line['geneticOrigin']]
                    }
                )
                batch.sources.add(source)

                gfs = GeneticFeatures.objects.create(
                    sample_id=line['sample_id'],
                    isolate=line['isolate'],
                    bp=line['bp'],
                    definition=line['definition'],
                    data_file_division=line['data_file_division'],
                    published_date=parse_datetime(line['date']) if line['date'] else None,
                    collection_date=parse_datetime(line['collection_date']) if line['collection_date'] else None,
                    molecule_type=line['molecule_type'],
                    sequence_version=line['sequence_version'],
                )

                gfs.references.add(batch)

                for production in line['genetic_features']:
                    gene = None
                    product = None
                    if production['gene']:
                        genesyn, _ = Synonym.objects.get_or_create(name=production['gene'])
                        gene = Gene.objects.filter(synonyms=genesyn).first()
                        if not gene:
                            gene = Gene.objects.create(accepted=genesyn)
                        # gene, _ = Gene.objects.get_or_create(synonyms=genesyn, defaults={'accepted': genesyn})
                        gene.references.add(batch)
                    if production['product']:
                        prodsyn, _ = Synonym.objects.get_or_create(name=production['product'])
                        product = Product.objects.filter(synonyms=prodsyn).first()
                        if not product:
                            product = Product.objects.create(accepted=prodsyn)
                        # product, _ = Product.objects.get_or_create(synonyms=prodsyn, defaults={'accepted': prodsyn})
                        product.references.add(batch)
                    prod_rel, _ = Produces.objects.get_or_create(
                        gene=gene,
                        product=product
                    )
                    prod_rel.references.add(batch)
                    gfs.products.add(prod_rel)

                taxonomy = TaxonomicLevel.objects.find(line['taxon'])

                assert taxonomy.count() == 1, f'Multiple taxonomy trees found for {line["taxon"]}'

                occ = Occurrence.objects.create(
                    voucher=line['voucher'] or '',
                    locality=line['locality'] or '',
                    latitude=line['lat_lon'][0] if line['lat_lon'] else '',
                    longitude=line['lat_lon'][1] if line['lat_lon'] else '',
                    collection_date=parse_datetime(line['collection_date']) if line['collection_date'] else None,
                    taxonomy=taxonomy.first(),
                    genetic_features=gfs
                )
                occ.references.add(batch)
