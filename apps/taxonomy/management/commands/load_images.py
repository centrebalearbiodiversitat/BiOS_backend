import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import TaxonomicLevel
from apps.versioning.models import OriginSource, Source, Batch

IMAGE = 3


@transaction.atomic
def add_taxonomic_image(line, batch):
	if not line["taxon"]:
		raise Exception("No taxon name")

	if line["image_id"]:
		taxon = TaxonomicLevel.objects.find(line["taxon"]).first()

		source = get_or_create_source("iNaturalist", "database", batch)
		# source = get_or_create_source(line["source"], line["origin"], batch)
		os, new_os = OriginSource.objects.get_or_create(origin_id=line["image_id"], source=source, attribution=line["attribution"])

		if taxon.images.filter(source=os.source, origin_id=os.origin_id).exists():
			raise Exception(f"Origin source id already existing. {os}\n{line}")
		taxon.images.add(os)

		taxon.save()


def get_or_create_source(source, origin, batch):
	if not source:
		raise Exception("All records must have a source")

	source, _ = Source.objects.get_or_create(
		name__iexact=source,
		data_type=IMAGE,  # Filter out 2 sources with the same name and data_type
		defaults={
			"name": source,
			"accepted": True,
			"origin": Source.TRANSLATE_CHOICES[origin],
			"data_type": IMAGE,  # data_type equal to 3 (IMAGE)
			"url": "https://inaturalist-open-data.s3.amazonaws.com/photos/{id}",
			"batch": batch,
		},
	)

	return source


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
			batch = Batch.objects.create()

			for line in csv_file:
				try:
					add_taxonomic_image(line, batch)
				except Exception as e:
					print(e)
					exception = True

			if exception:
				raise Exception("Errors found: Rollback control")
