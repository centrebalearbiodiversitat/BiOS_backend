import json
import os
import traceback
import re

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.taxonomy.models import TaxonomicLevel
from apps.tags.models import Habitat, IUCNData, System
from apps.versioning.models import Batch, OriginId, Source, Basis
from common.utils.utils import get_or_create_source, is_batch_referenced

EXTERNAL_ID = "origin_id"
IUCN = "IUCN"


def check_taxon(line):
	taxonomy = TaxonomicLevel.objects.find(taxon=line["origin_taxon"])

	if taxonomy.count() == 0:
		raise Exception(f"Taxonomy not found.\n{line}")
	elif taxonomy.count() > 1:
		raise Exception(f"Multiple taxonomy found.\n{line}")

	return taxonomy.first()


iucn_regex = re.compile(r"^[A-Z]{2}/[a-z]{2}$")


def transform_iucn_status(line):
	iucn_fields = ["iucn_global", "iucn_europe", "iucn_mediterranean"]
	for field in line.keys() & iucn_fields:
		if field in line and line[field]:
			if re.match(iucn_regex, line[field]):
				line[field] = line[field][-2:].upper()


def load_taxon_data_from_json(line, taxonomy, batch):
	os = None
	if line[EXTERNAL_ID]:
		source = get_or_create_source(
			source_type=Basis.DATABASE,
			extraction_method=Source.API,
			data_type=Source.TAXON_DATA,
			batch=batch,
			internal_name=IUCN,
		)
		os, new_source = OriginId.objects.get_or_create(external_id=line[EXTERNAL_ID], source=source)

	iucn_data, _ = IUCNData.objects.update_or_create(
		taxonomy=taxonomy,
		defaults={
			"iucn_global": IUCNData.TRANSLATE_CS[line["iucn_global"].lower()] if line["iucn_global"] else IUCNData.NE,
			"iucn_europe": IUCNData.TRANSLATE_CS[line["iucn_europe"].lower()] if line["iucn_europe"] else IUCNData.NE,
			"iucn_mediterranean": IUCNData.TRANSLATE_CS[line["iucn_mediterranean"].lower()] if line["iucn_mediterranean"] else IUCNData.NE,
			"batch": batch,
		},
	)

	if os:  # if there is data available
		habitat_ids = set(line["habitat"] or [])
		valid_habitats = Habitat.objects.filter(sources__external_id__in=habitat_ids)
		if len(valid_habitats) != len(habitat_ids):
			invalid_ids = habitat_ids - set(valid_habitats.values_list("sources__external_id", flat=True))
			raise Exception(f"Invalid habitat IDs: {invalid_ids}")
		iucn_data.habitats.set(valid_habitats)
		iucn_data.sources.add(os)

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
