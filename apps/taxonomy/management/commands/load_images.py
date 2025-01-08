import json

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import TaxonomicLevel
from apps.versioning.models import OriginId, Batch, Source
from common.utils.utils import get_or_create_source

EXTERNAL_ID = "image_id"
INATURALIST = "INaturalist"


def add_taxonomic_image(line, batch):
	if not line["taxon"]:
		print(f"Taxon does not exist\n{line}")
		return

	if line[EXTERNAL_ID]:
		taxon = TaxonomicLevel.objects.find(line["taxon"])
		taxon_count = taxon.count()
		if taxon_count == 0:
			raise Exception(f"Taxon not found.\n{line}")
		elif taxon_count > 1:
			raise Exception(f"Multiple taxa found\n{line}")

		taxon = taxon.first()

		source = get_or_create_source(source_type=Source.DATABASE, extraction_method=Source.API, data_type=Source.IMAGE, batch=batch, internal_name=INATURALIST)

		os, _ = OriginId.objects.get_or_create(external_id=line[EXTERNAL_ID], source=source, defaults={"attribution": line["attribution"]})

		if not taxon.images.filter(id=os.id):
			taxon.images.clear()
			taxon.images.add(os)

		taxon.save()


class Command(BaseCommand):
	help = "Loads taxon images from csv"

	def add_arguments(self, parser):
		parser.add_argument("file", type=str)

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		exception = False

		with open(file_name, encoding="utf-8") as file:
			data = json.load(file)
			batch = Batch.objects.create()

			for line in data:
				try:
					add_taxonomic_image(line, batch)
				except Exception as e:
					print(e)
					exception = True

			if exception:
				raise Exception("Errors found: Rollback control")
