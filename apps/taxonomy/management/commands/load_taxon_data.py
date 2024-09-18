import json
import traceback

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import Habitat, TaxonData, TaxonomicLevel


def check_taxon(line):
	taxonomy = TaxonomicLevel.objects.find(taxon=line["taxonomy"])

	if taxonomy.count() == 0:
		raise Exception(f"Taxonomy not found.\n{line}")
	elif taxonomy.count() > 1:
		raise Exception(f"Multiple taxonomy found.\n{line}")

	return taxonomy


def create_taxon_data(line, taxonomy):
	habitat_ids = set(line["habitat"] or [])

	valid_habitats = Habitat.objects.filter(sources__origin_id__in=habitat_ids)
	if len(valid_habitats) != len(habitat_ids):
		invalid_ids = habitat_ids - set(valid_habitats.values_list("sources__origin_id", flat=True))
		raise Exception(f"Invalid habitat IDs: {invalid_ids}")

	taxon_data, _ = TaxonData.objects.get_or_create(
		taxonomy=taxonomy.first(),
		defaults={
			"iucn_global": TaxonData.TRANSLATE_CS[line["iucn_global"].lower()] if line["iucn_global"] else TaxonData.NE,
			"iucn_europe": TaxonData.TRANSLATE_CS[line["iucn_europe"].lower()] if line["iucn_europe"] else TaxonData.NE,
			"iucn_mediterranean": TaxonData.TRANSLATE_CS[line["iucn_mediterranean"].lower()]
			if line["iucn_mediterranean"]
			else TaxonData.NE,
			"invasive": False,
			"domesticated": False,
			"freshwater": line["freshwater"],
			"marine": line["marine"],
			"terrestrial": line["terrestrial"],
		},
	)

	taxon_data.habitat.set(valid_habitats)
	taxon_data.save()


def add_taxon_data(line):
	taxonomy = check_taxon(line)
	create_taxon_data(line, taxonomy)


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument("file", type=str)

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		exception = False

		with open(file_name, "r") as file:
			json_data = json.load(file)

			for line in json_data:
				try:
					add_taxon_data(line)
				except:
					exception = True
					print(traceback.format_exc(), line)

		if exception:
			raise Exception("Errors found: Rollback control")
