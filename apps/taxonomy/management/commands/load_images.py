import csv
import json

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import TaxonomicLevel
from apps.versioning.models import OriginSource, Source, Batch


def add_taxonomic_image(line, batch):
	if not line["taxon"]:
		print(f"Taxon does not exist\n{line}")
		return

	if line["image_id"]:
		taxon = TaxonomicLevel.objects.find(line["taxon"])
		taxon_count = taxon.count()
		if taxon_count == 0:
			raise Exception(f"Taxon not found.\n{line}")
		elif taxon_count > 1:
			raise Exception(f"Multiple taxa found\n{line}")

		taxon = taxon.first()

		source = get_or_create_source("iNaturalist", "database", batch)
		# source = get_or_create_source(line["source"], line["origin"], batch)
		os, new_os = OriginSource.objects.get_or_create(origin_id=line["image_id"], source=source, defaults={"attribution": line["attribution"]})

		if not taxon.images.filter(id=os.id):
			taxon.images.clear()
			taxon.images.add(os)

		taxon.save()


def get_or_create_source(source, origin, batch):
	if not source:
		raise Exception(f"All records must have a source\n{source} {origin} {batch}")

	source, _ = Source.objects.get_or_create(
		name__iexact=source,
		data_type=Source.IMAGE,  # Filter out 2 sources with the same name and data_type
		defaults={
			"name": source,
			"accepted": True,
			"origin": Source.TRANSLATE_CHOICES[origin],
			"data_type": Source.IMAGE,  # data_type equal to 3 (IMAGE)
			"url": "https://inaturalist-open-data.s3.amazonaws.com/photos/{id}",
			"batch": batch,
		},
	)

	return source


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
