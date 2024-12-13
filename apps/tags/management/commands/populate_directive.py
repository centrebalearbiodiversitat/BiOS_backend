import csv

from apps.taxonomy.models import TaxonomicLevel
from apps.tags.models import Directive
from apps.versioning.models import Batch, OriginId, Source
from django.core.management.base import BaseCommand
from django.db import transaction
from common.utils.utils import get_or_create_source


BOOL_DICT = {"verdadero": True, "falso": False}


class Command(BaseCommand):
	help = "Loads directives from a CSV file"

	def add_arguments(self, parser):
		parser.add_argument("csv_file", type=str, help="Path to the CSV file")

	@transaction.atomic
	def handle(self, *args, **options):
		csv_file_name = options["csv_file"]
		batch = Batch.objects.create()

		with open(csv_file_name, "r") as csv_file:
			reader = csv.DictReader(csv_file)

			for line in reader:
				taxon_name = line["origin_taxon"]
				taxonomy = TaxonomicLevel.objects.find(taxon=taxon_name).first()
				
				source = get_or_create_source(
					source_type=Source.DATABASE,
					extraction_method=Source.API,
					data_type=Source.TAXON,
					batch=batch,
					internal_name=line["source"],
				)
				
				os, new_source = OriginId.objects.get_or_create(source=source)

				directive, _ = Directive.objects.update_or_create(
					taxon_name=line["origin_taxon"],
					defaults={
						"taxonomy": taxonomy,
						"cites": BOOL_DICT.get(line["cites"].lower()),
						"ceea": BOOL_DICT.get(line["ceea"].lower()),
						"lespre": BOOL_DICT.get(line["lespre"].lower()),
						"directiva_aves": BOOL_DICT.get(line["directiva_aves"].lower()),
						"directiva_habitats": BOOL_DICT.get(line["directiva_habitats"].lower()),
						"batch": batch,
					},
				)
				directive.sources.add(os)

		self.stdout.write(self.style.SUCCESS("Successfully created directives"))
