import csv
import json
import traceback
import re
from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.taxonomy.models import Habitat, Tag, TaxonData, TaxonomicLevel
from apps.versioning.models import Batch, Source, OriginSource
from apps.taxonomy.management.commands.populate_tags import TAGS


def check_taxon(line):
	taxonomy = TaxonomicLevel.objects.find(taxon=line["origin_taxon"])

	if taxonomy.count() == 0:
		raise Exception(f"Taxonomy not found.\n{line}")
	elif taxonomy.count() > 1:
		raise Exception(f"Multiple taxonomy found.\n{line}")

	return taxonomy


iucn_regex = re.compile(r"^[A-Z]{2}/[a-z]{2}$")


def transform_iucn_status(line):
	iucn_fields = ["iucn_global", "iucn_europe", "iucn_mediterranean"]
	for field in line.keys() & iucn_fields:
		if field in line and line[field]:
			if re.match(iucn_regex, line[field]):
				line[field] = line[field][-2:].upper()


def create_taxon_data_from_json(line, taxonomy, batch):
	habitat_ids = set(line["habitat"] or [])

	valid_habitats = Habitat.objects.filter(sources__origin_id__in=habitat_ids)
	if len(valid_habitats) != len(habitat_ids):
		invalid_ids = habitat_ids - set(valid_habitats.values_list("sources__origin_id", flat=True))
		raise Exception(f"Invalid habitat IDs: {invalid_ids}")

	transform_iucn_status(line)

	taxon_data, _ = TaxonData.objects.get_or_create(
		taxonomy=taxonomy.first(),
		defaults={
			"iucn_global": TaxonData.TRANSLATE_CS[line["iucn_global"].lower()] if line["iucn_global"] else TaxonData.NE,
			"iucn_europe": TaxonData.TRANSLATE_CS[line["iucn_europe"].lower()] if line["iucn_europe"] else TaxonData.NE,
			"iucn_mediterranean": TaxonData.TRANSLATE_CS[line["iucn_mediterranean"].lower()] if line["iucn_mediterranean"] else TaxonData.NE,
			"batch": batch,
		},
	)

	taxon_data.habitat.set(valid_habitats)

	source, _ = Source.objects.get_or_create(
		name__iexact=line["source"],
		data_type=Source.TAXON,
		defaults={
			"name": line["source"],
			"accepted": True,
			"origin": Source.TRANSLATE_CHOICES[line["origin"]],
			"data_type": Source.TAXON,
			"url": None,
		},
	)

	os, new_source = OriginSource.objects.get_or_create(origin_id="unknown", source=source)

	taxon_data.sources.add(os)

	taxon_data.save()


def update_taxon_data_from_csv(line, taxonomy, batch):
	taxon_data, _ = TaxonData.objects.get_or_create(
		taxonomy=taxonomy.first(),
		defaults={"batch": batch},
	)

	doe_value = line.get("degreeOfEstablishment")

	try:
		doe_tag = next(tag for tag in TAGS if tag[0] == doe_value and tag[1] == Tag.DOE)
		taxon_data.tags.add(Tag.objects.get(name=doe_tag[0], tag_type=doe_tag[1]))
	except StopIteration:
		raise Exception(f"No Tag.DOE was found with the value '{doe_value}'")

	taxon_data.freshwater = line["freshwater"].capitalize()
	taxon_data.marine = line["marine"].capitalize()
	taxon_data.terrestrial = line["terrestrial"].capitalize()

	taxon_data.save()


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument("file", type=str, help="Path to the data file")

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		file_format = file_name
		exception = False
		batch = Batch.objects.create()

		if file_format == "json":
			with open(file_name, "r") as json_file:
				json_data = json.load(json_file)

				for line in json_data:
					try:
						taxonomy = check_taxon(line)
						create_taxon_data_from_json(line, taxonomy, batch)
					except:
						exception = True
						print(traceback.format_exc(), line)
		elif file_format == "csv":
			with open(file_name, "r") as csv_file:
				reader = csv.DictReader(csv_file)

				for line in reader:
					try:
						taxonomy = check_taxon(line)
						update_taxon_data_from_csv(line, taxonomy, batch)
					except Exception as e:
						exception = True
						print(traceback.format_exc(), line)
						error_message = str(e)
		else:
			raise CommandError("You must specify the file format using --format=json or --format=csv")

		if exception:
			raise Exception(f"Errors found: Rollback control\n{error_message}")
