import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import TaxonomicLevel


@transaction.atomic
def add_taxonomic_image(line):
	if not line["taxon"]:
		raise Exception("No taxon name")

	if line["image_id"]:
		taxon = TaxonomicLevel.objects.find(line["taxon"]).first()
		taxon.image_id = line["url"]
		taxon.attribution = line["attribution"]
		taxon.save()


class Command(BaseCommand):
	help = "Loads taxon images from csv"

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

			for line in csv_file:
				try:
					add_taxonomic_image(line)
				except:
					exception = True

			if exception:
				raise Exception("Errors found: Rollback control")