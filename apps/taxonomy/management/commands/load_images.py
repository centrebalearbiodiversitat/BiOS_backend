import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import TaxonomicLevel
from apps.versioning.models import Batch


@transaction.atomic
def add_taxonomic_image(line):
    if not line["taxon"]:
        return "No taxon name"

    taxon_query = TaxonomicLevel.objects.find(line["taxon"])
    taxon = taxon_query.first() if taxon_query.exists() else None

    if taxon:
        taxon.image_path = line["image_path"]
        taxon.attribution = line["attribution"]
        taxon.save()

    return taxon

class Command(BaseCommand):
	help = "Loads taxon image from csv"

	def add_arguments(self, parser):
		parser.add_argument("file", type=str)
		parser.add_argument("-d", nargs="?", type=str, default=",")

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		delimiter = options["d"]
		exception = False
		with open(file_name, encoding="utf-8") as file:
			csv_file = csv.DictReader(file, delimiter=delimiter)
			batch = Batch.objects.create()

			for line in csv_file:

				try:
					add_taxonomic_image(line, batch)
				except:
					exception = True

			if exception:
				raise Exception("Errors found: Rollback control")
