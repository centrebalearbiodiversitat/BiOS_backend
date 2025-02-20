import traceback
from openpyxl import load_workbook

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.taxonomy.models import TaxonomicLevel
from apps.tags.models import Tag, TaxonTag, System, Directive
from apps.versioning.models import Batch, OriginId, Source
from common.utils.utils import get_or_create_source

EXTERNAL_ID = "origin_id"
INTERNAL_NAME = "source"
SOURCE_TYPE = "origin"


def check_taxon(line):
	taxonomy = TaxonomicLevel.objects.find(taxon=line["origin_taxon"])

	if taxonomy.count() == 0:
		raise Exception(f"Taxonomy not found.\n{line}")
	elif taxonomy.count() > 1:
		raise Exception(f"Multiple taxonomy found.\n{line}")

	return taxonomy.first()


def load_taxon_tags(line, taxonomy, batch):
	if line["taxon_rank"] not in ["species", "subspecies", "variety"]:
		raise Exception(f"Taxon rank not allowed.\n{line}")

	source = get_or_create_source(
		source_type=Source.TRANSLATE_SOURCE_TYPE[line[SOURCE_TYPE].lower()],
		extraction_method=Source.EXPERT,
		data_type=Source.TAXON_DATA,
		batch=batch,
		internal_name=line[INTERNAL_NAME],
	)

	try:
		system = System.objects.get(taxonomy=taxonomy)
	except System.DoesNotExist:
		raise Exception(f"Taxon systems not found. Taxon data (iucn) not loaded yet?\n{line}")

	os, _ = OriginId.objects.get_or_create(source=source)
	# if the 3 systems are None, it means IUCN has no available data
	if system.freshwater is None and system.marine is None and system.terrestrial is None:
		system.freshwater = line["freshwater"]
		system.marine = line["marine"]
		system.terrestrial = line["terrestrial"]
		system.sources.clear()
		system.sources.add(os)
		system.save()

	doe_value = line.get("degreeOfEstablishment")
	try:
		doe_tag = Tag.objects.get(name=doe_value, tag_type=Tag.DOE)
		taxon_tag, _ = TaxonTag.objects.get_or_create(
			taxonomy=taxonomy,
			tag=doe_tag,
			defaults={"batch": batch},
		)
		taxon_tag.sources.add(os)
	except Tag.DoesNotExist:
		raise Exception(f"No Tag.DOE was found with the value '{doe_value}'")

	directive, _ = Directive.objects.get_or_create(
		taxonomy=taxonomy,
		defaults={
			"cites": line["cites"],
			"ceea": line["ceea"],
			"lespre": line["lespre"],
			"directiva_aves": line["directiva_aves"],
			"directiva_habitats": line["directiva_habitats"],
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
		exception = False
		batch = Batch.objects.create()

		try:
			reader = load_workbook(file_name)
			sheet = reader.active
			headers = [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))]
			for row in sheet.iter_rows(min_row=2, values_only=True):
				line = dict(zip(headers, row))
				try:
					taxonomy = check_taxon(line)
					load_taxon_tags(line, taxonomy, batch)
				except:
					exception = True
					print(traceback.format_exc(), line)
		except FileNotFoundError:
			exception = True
			print("No such file or directory")

		if exception:
			raise Exception(f"Errors found: Rollback control")
