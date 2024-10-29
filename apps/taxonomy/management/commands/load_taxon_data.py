import json
import traceback
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.taxonomy.models import Habitat, Tag, TaxonData, TaxonomicLevel
from apps.versioning.models import Batch, Source, OriginSource
from apps.taxonomy.management.commands.populate_tags import TAGS


def check_taxon(line):
	taxonomy = TaxonomicLevel.objects.find(taxon=line["taxonomy"])

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


def create_taxon_data(line, taxonomy, batch):
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
			"iucn_mediterranean": TaxonData.TRANSLATE_CS[line["iucn_mediterranean"].lower()]
			if line["iucn_mediterranean"]
			else TaxonData.NE,
			"freshwater": line["freshwater"],
			"marine": line["marine"],
			"terrestrial": line["terrestrial"],
			"batch": batch,
		},
	)

	taxon_data.habitat.set(valid_habitats)

	existing_tags = Tag.objects.all()

	for tag in existing_tags:
		if line.get(tag.name) is True:
			if tag.tag_type == Tag.DOE:
				if taxon_data.tags.filter(tag_type=Tag.DOE, name__in=[t[0] for t in TAGS if t[1] == Tag.DOE]).exists():
					raise Exception(f"Cannot add DOE tag '{tag.name}' to taxon_data {taxon_data.id} as another DOE tag already exists.")
			taxon_data.tags.add(tag)

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


def add_taxon_data(line, batch):
	taxonomy = check_taxon(line)
	create_taxon_data(line, taxonomy, batch)


class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument("file", type=str)

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		exception = False
		batch = Batch.objects.create()

		with open(file_name, "r") as file:
			json_data = json.load(file)

			for line in json_data:
				try:
					add_taxon_data(line, batch)
				except:
					exception = True
					print(traceback.format_exc(), line)

		if exception:
			raise Exception("Errors found: Rollback control")
