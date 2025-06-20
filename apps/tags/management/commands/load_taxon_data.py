import json
import os
import traceback
import re

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.taxonomy.models import TaxonomicLevel
from apps.tags.models import Habitat, IUCNData, System, HabitatTaxonomy
from apps.versioning.models import Batch, OriginId, Source
from common.utils.utils import get_or_create_source, is_batch_referenced


INTERNAL_NAME = "IUCN"
EXTERNAL_ID = "origin_id"
IUCN_FIELDS = ["iucn_global", "iucn_europe", "iucn_mediterranean"]

def check_taxon(line):
	taxonomy = TaxonomicLevel.objects.find(taxon=line["origin_taxon"])

	if taxonomy.count() == 0:
		raise Exception(f"Taxonomy not found.\n{line}")
	elif taxonomy.count() > 1:
		raise Exception(f"Multiple taxonomy found.\n{line}")

	return taxonomy.first()


iucn_regex = re.compile(r"^[A-Z]{2}/[a-z]{2}$")


def transform_iucn_status(line):
	for field in IUCN_FIELDS:
		if isinstance(line.get(field), dict):  # Check if the iucn_fields exists into the line and check if line is a dictionary
			nested_dict = line[field]

			if "status" in nested_dict and nested_dict["status"] is not None:
				current_status_value = str(nested_dict["status"])

				# Check if the status value matches the expected regex pattern
				if re.match(iucn_regex, current_status_value):
					nested_dict["status"] = current_status_value[-2:].upper()


def load_taxon_data_from_json(line, taxonomy, batch):
	os = None
	taxon_id = line.get(EXTERNAL_ID)

	try:
		with transaction.atomic():
			for field in IUCN_FIELDS:
				field_data = line.get(field)
				if not field_data:
					continue

				status = field_data.get("status")
				url = field_data.get("url")

				if status is None or not url:
					continue

				url_id = url.rstrip("/").split("/")[-1]

				if not url_id:
					continue

				region_key = field.split("_")[1].lower()
				region = IUCNData.TRANSLATE_RG.get(region_key)

				assessment = IUCNData.TRANSLATE_CS.get(status.lower(), IUCNData.NE)

				iucn_data, _ = IUCNData.objects.update_or_create(
					taxonomy=taxonomy,
					region=region,
					defaults={
						"assessment": assessment,
						"batch": batch,
					}
				)

				source = get_or_create_source(
					source_type=Source.DATABASE,
					extraction_method=Source.API,
					data_type=Source.TAXON_DATA,
					batch=batch,
					internal_name=INTERNAL_NAME,
				)

				origin, _ = OriginId.objects.get_or_create(
					external_id=f"{taxon_id}/{url_id}",
					source=source
				)

				iucn_data.sources.add(origin)
	except Exception as e:
		print(f"⚠️ Error in field '{field}': {e}")

	if os:
		habitat_ids = set(line["habitat"] or [])
		valid_habitats = Habitat.objects.filter(sources__external_id__in=habitat_ids)

		if len(valid_habitats) != len(habitat_ids):
			invalid_ids = habitat_ids - set(valid_habitats.values_list("sources__external_id", flat=True))
			raise Exception(f"Invalid habitat IDs: {invalid_ids}")

		for single_habitat_object in valid_habitats:
			habitat_data, _ = HabitatTaxonomy.objects.update_or_create(
				taxonomy=taxonomy,
				habitat=single_habitat_object,
				defaults={
					"batch": batch,
				}
			)
			habitat_data.sources.add(os)

	system, _ = System.objects.update_or_create(
		taxonomy=taxonomy,
		defaults={
			"freshwater": line["freshwater"],
			"marine": line["marine"],
			"terrestrial": line["terrestrial"],
			"batch": batch,
		},
	)
	if os:  # if there is data available
		system.sources.add(os)


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument("file", type=str, help="Path to the data file")

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		_, file_format = os.path.splitext(file_name)

		exception = False
		batch = Batch.objects.create()

		with open(file_name, "r") as json_file:
			json_data = json.load(json_file)

			# line = json_data[0]

			for line in json_data:
				try:
					transform_iucn_status(line)
					taxonomy = check_taxon(line)
					load_taxon_data_from_json(line, taxonomy, batch)
				except:
					exception = True
					print(traceback.format_exc(), line)

		if exception:
			raise Exception(f"Errors found: Rollback control")

		is_batch_referenced(batch)
