import csv
import json
import os
import traceback
import re
from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.taxonomy.models import TaxonomicLevel
from apps.tags.models import Habitat, Tag, TaxonTag, IUCNData, System, Directive
from apps.versioning.models import Batch, OriginId, Source
from common.utils.utils import get_or_create_source

BOOL_DICT = {"verdadero": True, "falso": False}
EXTERNAL_ID = "origin_id"
INTERNAL_NAME = "source"
IUCN = "IUCN"
SOURCE_TYPE = "origin"
URL = "origin_url"


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


def load_taxon_data_from_json(line, taxonomy, batch):
	source = get_or_create_source(
		source_type=Source.DATABASE,
		extraction_method=Source.API,
		data_type=Source.TAXON_DATA,
		batch=batch,
		internal_name=IUCN,
	)
	os, new_source = OriginId.objects.get_or_create(external_id=line[EXTERNAL_ID], source=source)

	habitat_ids = set(line["habitat"] or [])
	valid_habitats = Habitat.objects.filter(sources__external_id__in=habitat_ids)
	if len(valid_habitats) != len(habitat_ids):
		invalid_ids = habitat_ids - set(valid_habitats.values_list("sources__external_id", flat=True))
		raise Exception(f"Invalid habitat IDs: {invalid_ids}")

	iucn_data, _ = IUCNData.objects.update_or_create(
		taxonomy=taxonomy.first(),
		defaults={
			"iucn_global": IUCNData.TRANSLATE_CS[line["iucn_global"].lower()] if line["iucn_global"] else IUCNData.NE,
			"iucn_europe": IUCNData.TRANSLATE_CS[line["iucn_europe"].lower()] if line["iucn_europe"] else IUCNData.NE,
			"iucn_mediterranean": IUCNData.TRANSLATE_CS[line["iucn_mediterranean"].lower()] if line["iucn_mediterranean"] else IUCNData.NE,
			"batch": batch,
		},
	)

	iucn_data.habitat.set(valid_habitats)
	iucn_data.sources.add(os)

	system, _ = System.objects.update_or_create(
		taxonomy=taxonomy.first(),
		defaults={
			"freshwater": line["freshwater"],
			"marine": line["marine"],
			"terrestrial": line["terrestrial"],
			"batch": batch,
		},
	)
	system.sources.add(os)


def load_taxon_data_from_csv(line, taxonomy, batch):
	if line["taxon_rank"] in ["species", "subspecies", "variety"]:
		source = get_or_create_source(
			source_type=Source.TRANSLATE_SOURCE_TYPE[line[SOURCE_TYPE].lower()],
			extraction_method=Source.EXPERT,
			data_type=Source.TAXON_DATA,
			batch=batch,
			internal_name=line[INTERNAL_NAME],
		)
		system = System.objects.get(taxonomy=taxonomy.first())

		os, _ = OriginId.objects.get_or_create(source=source)
		if system.freshwater is None and system.marine is None and system.terrestrial is None:
			system.freshwater = BOOL_DICT.get(line["freshwater"].lower(), None)
			system.marine = BOOL_DICT.get(line["marine"].lower(), None)
			system.terrestrial = BOOL_DICT.get(line["terrestrial"].lower(), None)
			system.sources.clear()
			system.sources.add(os)
			system.save()

		taxon_tag, _ = TaxonTag.objects.get_or_create(
			taxonomy=taxonomy.first(),
			defaults={"batch": batch},
		)
		taxon_tag.sources.add(os)

		doe_value = line.get("degreeOfEstablishment")
		try:
			doe_tag = Tag.objects.get(name=doe_value, tag_type=Tag.DOE)
			taxon_tag.tags.add(doe_tag)
		except Tag.DoesNotExist:
			raise Exception(f"No Tag.DOE was found with the value '{doe_value}'")

		directive, _ = Directive.objects.get_or_create(
			taxon_name=line["origin_taxon"],
			defaults={
				"taxonomy": taxonomy.first(),
				"cites": BOOL_DICT.get(line["cites"].lower(), None),
				"ceea": BOOL_DICT.get(line["ceea"].lower(), None),
				"lespre": BOOL_DICT.get(line["lespre"].lower(), None),
				"directiva_aves": BOOL_DICT.get(line["directiva_aves"].lower(), None),
				"directiva_habitats": BOOL_DICT.get(line["directiva_habitats"].lower(), None),
				"batch": batch,
			},
		)
		directive.sources.add(os)


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument("file", type=str, help="Path to the data file")
		parser.add_argument("-d", nargs="?", type=str, default=";")

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		_, file_format = os.path.splitext(file_name)

		exception = False
		file_format = file_format.lower()
		batch = Batch.objects.create()

		if file_format == ".json":
			with open(file_name, "r") as json_file:
				json_data = json.load(json_file)

				for line in json_data:
					try:
						taxonomy = check_taxon(line)
						load_taxon_data_from_json(line, taxonomy, batch)
					except:
						exception = True
						print(traceback.format_exc(), line)
		elif file_format == ".csv":
			delimiter = options["d"]

			with open(file_name, "r") as csv_file:
				reader = csv.DictReader(csv_file, delimiter=delimiter)

				for line in reader:
					try:
						taxonomy = check_taxon(line)
						load_taxon_data_from_csv(line, taxonomy, batch)
					except Exception as e:
						exception = True
						print(traceback.format_exc(), line)
		else:
			raise CommandError("You must upload a file in JSON or CSV format.")

		if exception:
			raise Exception(f"Errors found: Rollback control")
