import csv
import json
import traceback
import re
from django.core.management import CommandError
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.taxonomy.models import Habitat, Tag, TaxonTag, TaxonomicLevel, IUCNData, System
from apps.versioning.models import Batch, Source, OriginSource
from apps.taxonomy.management.commands.populate_tags import TAGS

BOOL_DICT = {
	"verdadero": True,
	"falso": False
}

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
	
	habitat_ids = set(line["habitat"] or [])

	valid_habitats = Habitat.objects.filter(sources__origin_id__in=habitat_ids)
	if len(valid_habitats) != len(habitat_ids):
		invalid_ids = habitat_ids - set(valid_habitats.values_list("sources__origin_id", flat=True))
		raise Exception(f"Invalid habitat IDs: {invalid_ids}")
	
	iucn_data, _ = IUCNData.objects.update_or_create(
		taxonomy=taxonomy.first(),
		defaults={
			"iucn_global": IUCNData.TRANSLATE_CS[line["iucn_global"].lower()] if line["iucn_global"] else IUCNData.NE,
			"iucn_europe": IUCNData.TRANSLATE_CS[line["iucn_europe"].lower()] if line["iucn_europe"] else IUCNData.NE,
			"iucn_mediterranean": IUCNData.TRANSLATE_CS[line["iucn_mediterranean"].lower()]
			if line["iucn_mediterranean"]
			else IUCNData.NE,
			"habit"
			"batch": batch,
		},
	)

	iucn_data.habitat.set(valid_habitats)

	# System Data
	System.objects.update_or_create(
		taxonomy=taxonomy.first(),
		defaults={
			"freshwater": line["freshwater"],
			"marine": line["marine"],
			"terrestrial": line["terrestrial"],
			"batch": batch,
		},
	)

def load_taxon_data_from_csv(line, taxonomy, batch):
	if line["taxon_rank"] in ["species", "subspecies", "variety"]:
		taxon_tag, _ = TaxonTag.objects.get_or_create(
		taxonomy=taxonomy.first(),
		defaults={"batch": batch},
		)

		doe_value = line.get('degreeOfEstablishment')

		try:
			doe_tag = next(tag for tag in TAGS if tag[0] == doe_value and tag[1] == Tag.DOE)
			taxon_tag.tags.add(Tag.objects.get(name=doe_tag[0], tag_type=doe_tag[1]))
		except StopIteration:
			raise Exception(f"No Tag.DOE was found with the value '{doe_value}'")

		system, created = System.objects.get_or_create(
			taxonomy=taxonomy.first(),
			sources__source__name__iexact=line["source_1"],
			sources__source__origin=Source.TRANSLATE_CHOICES[line["origin_1"]],
			sources__source__data_type=Source.TAXON,
			defaults={
					"freshwater": BOOL_DICT.get(line["freshwater"].lower(), None),
					"marine": BOOL_DICT.get(line["marine"].lower(), None),
					"terrestrial": BOOL_DICT.get(line["terrestrial"].lower(), None),
					"batch": batch,
				},
		)

		
		if created:
			source, _ = Source.objects.get_or_create(
				name__iexact=line["source_1"],
				data_type=Source.TAXON,
				defaults={
					"name": line["source_1"],
					"accepted": True,
					"origin": Source.TRANSLATE_CHOICES[line["origin_1"]],
					"data_type": Source.TAXON,
					"url": None,
				},
			)
			os, new_source = OriginSource.objects.get_or_create(origin_id="unknown", source=source)
			system.sources.add(os)
		
		else:
			if system.freshwater is None and system.marine is None and system.terrestrial is None:
				system.freshwater = BOOL_DICT.get(line["freshwater"].lower(), None)
				system.marine = BOOL_DICT.get(line["marine"].lower(), None)
				system.terrestrial = BOOL_DICT.get(line["terrestrial"].lower(), None)	
				source, _ = Source.objects.get_or_create(
					name__iexact=line["source_2"],
					data_type=Source.TAXON,
					defaults={
						"name": line["source_2"],
						"accepted": True,
						"origin": Source.TRANSLATE_CHOICES[line["origin_2"]],
						"data_type": Source.TAXON,
						"url": None,
					},
				)
				system.sources.clear()
				os, new_source = OriginSource.objects.get_or_create(origin_id="unknown", source=source)
				system.sources.add(os)
				system.save()

			
class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument("file", type=str, help="Path to the data file")  
		parser.add_argument("--format", choices=["json", "csv"], help="File format (json or csv)") 

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		file_format = options.get("format")
		exception = False
		batch = Batch.objects.create()

		if file_format == "json":
			with open(file_name, "r") as json_file:
				json_data = json.load(json_file)

				for line in json_data:
					try:
						taxonomy = check_taxon(line)
						load_taxon_data_from_json(line, taxonomy, batch)
					except:
						exception = True
						print(traceback.format_exc(), line)
		elif file_format == "csv":
			with open(file_name, "r") as csv_file:
				reader = csv.DictReader(csv_file)

				for line in reader:
					try:
						taxonomy = check_taxon(line)
						load_taxon_data_from_csv(line, taxonomy, batch)
					except Exception as e:
						exception = True
						print(traceback.format_exc(), line)
						error_message = str(e)
		else:
			raise CommandError("You must specify the file format using --format json or --format csv")

		if exception:
			raise Exception(f"Errors found: Rollback control\n{error_message}")
