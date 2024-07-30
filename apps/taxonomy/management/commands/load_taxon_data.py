import csv
import re

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import Habitat, TaxonData, TaxonomicLevel


def check_taxon(line):
	taxonomy = TaxonomicLevel.objects.find(taxon=line["originalName"])
	if taxonomy.count() == 0:
		raise Exception(f"Taxonomy not found.\n{line}")
	elif taxonomy.count() > 1:
		raise Exception(f"Multiple taxonomy found.\n{line}")
	return taxonomy


def create_taxon_data(line, taxonomy):
	habitat_string = line.get("habitat", "")
	# Separate by commas, but not inside parentheses
	habitat_names = re.split(r",\s*(?![^()]*\))", habitat_string)

	habitats = []
	for name in habitat_names:
		habitat, _ = Habitat.objects.get_or_create(name=name.strip())
		habitats.append(habitat)

	iucn_global_value = TaxonData.TRANSLATE_CS.get(line.get("iucnStatusGlobal"), TaxonData.NE)
	iucn_europe_value = TaxonData.TRANSLATE_CS.get(line.get("iucnStatusEurope"), TaxonData.NE)
	iucn_mediterranean_value = TaxonData.TRANSLATE_CS.get(line.get("iucnStatusMediterranean"), TaxonData.NE)

	taxon_data, created = TaxonData.objects.get_or_create(
		taxonomy=taxonomy.first(),
		defaults={
			"iucn_global": iucn_global_value,
			"iucn_europe": iucn_europe_value,
			"iucn_mediterranean": iucn_mediterranean_value,
			"invasive": line.get("invasive").lower() == "true",
			"domesticated": line.get("domesticated").lower() == "true",
			"freshwater": line.get("freshwater").lower() == "true",
			"marine": line.get("marine").lower() == "true",
			"terrestrial": line.get("terrestrial").lower() == "true",
		},
	)

	if not created:
		taxon_data.iucn_global = iucn_global_value
		taxon_data.iucn_europe = iucn_europe_value
		taxon_data.iucn_mediterranean = iucn_mediterranean_value
		taxon_data.invasive = line.get("invasive").lower() == "true"
		taxon_data.domesticated = line.get("domesticated").lower() == "true"
		taxon_data.freshwater = line.get("freshwater").lower() == "true"
		taxon_data.marine = line.get("marine").lower() == "true"
		taxon_data.terrestrial = line.get("terrestrial").lower() == "true"
		taxon_data.save()

	taxon_data.habitat.set(habitats)
	taxon_data.save()


def add_taxon_data(line):
	try:
		taxonomy = check_taxon(line)
		create_taxon_data(line, taxonomy)
	except Exception as e:
		print("Error processing line")
		print(e)


class Command(BaseCommand):
	help = "Loads taxon data from a predefined list"

	def add_arguments(self, parser):
		parser.add_argument("file", type=str)
		parser.add_argument("-d", nargs="?", type=str, default=";")

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		delimiter = options["d"]
		with open(file_name, encoding="windows-1252") as file:
			csv_file = csv.DictReader(file, delimiter=delimiter)
			for line in csv_file:
				add_taxon_data(line)
