import json
import os
import traceback
import re

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.taxonomy.models import TaxonomicLevel
from apps.tags.models import Habitat, IUCNData, System, HabitatTaxonomy
from apps.versioning.models import Batch, OriginId, Source, Basis
from common.utils.utils import get_or_create_source, is_batch_referenced


INTERNAL_NAME = "IUCN"
EXTERNAL_ID = "origin_id"
IUCN_FIELDS = ["iucn_global", "iucn_europe", "iucn_mediterranean"]

iucn_regex = re.compile(r"^[A-Z]{2}/[a-z]{2}$")


def check_taxon(line):
	taxonomy = TaxonomicLevel.objects.find(taxon=line["origin_taxon"])

	if taxonomy.count() == 0:
		raise Exception(f"Taxonomy not found.\n{line}")
	elif taxonomy.count() > 1:
		raise Exception(f"Multiple taxonomy found.\n{line}")

	return taxonomy.first()


def transform_iucn_status(line):
	for field in IUCN_FIELDS:
		# Check if the IUCN_FIELDS exists into the line and check if line is a dictionary
		if isinstance(line.get(field), dict):
			nested_dict = line[field]

			if "status" in nested_dict and nested_dict["status"] is not None:
				current_status_value = str(nested_dict["status"])

				# Check if the status value matches the expected regex pattern
				if re.match(iucn_regex, current_status_value):
					nested_dict["status"] = current_status_value[-2:].upper()


# Important: This is valid only for IUCN json files.
def load_taxon_data_from_json(line, taxonomy, batch):
	taxon_id = line.get(EXTERNAL_ID)

	source = get_or_create_source(
		source_type=Basis.DATABASE,
		extraction_method=Source.API,
		data_type=Source.TAXON_DATA,
		batch=batch,
		internal_name=INTERNAL_NAME,
	)

	try:
		with transaction.atomic():
			# Assessment
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

				origin, _ = OriginId.objects.get_or_create(
					external_id=f"{taxon_id}/{url_id}",
					source=source
				)

				iucn_data.sources.add(origin)

		# System
		system, _ = System.objects.update_or_create(
			taxonomy=taxonomy,
			defaults={
				"freshwater": line["freshwater"],
				"marine": line["marine"],
				"terrestrial": line["terrestrial"],
				"batch": batch,
			}
		)

		origin, _ = OriginId.objects.get_or_create(source=source, external_id=taxon_id)
		system.sources.add(origin)

		# Habitats
		habitat_ids = set(line["habitat"] or [])
		valid_habitats = Habitat.objects.filter(sources__external_id__in=habitat_ids)

		if len(valid_habitats) != len(habitat_ids):
			invalid_ids = habitat_ids - set(valid_habitats.values_list("sources__external_id", flat=True))
			raise Exception(f"Invalid habitat IDs: {invalid_ids}")

		for single_habitat_object in valid_habitats:
			habitat_taxonomy, _ = HabitatTaxonomy.objects.update_or_create(
				taxonomy=taxonomy,
				habitat=single_habitat_object,
				defaults={
					"batch": batch
				}
			)

			origin, _ = OriginId.objects.get_or_create(source=source, external_id=taxon_id)
			habitat_taxonomy.sources.add(origin)

	except Exception as e:
		print(f"⚠️ Error in field '{field}': {e}")


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
