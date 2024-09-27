import csv
import re
import traceback

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import Authorship, TaxonomicLevel, TaxonData, Habitat
from apps.versioning.models import Batch, Source, OriginSource
from common.utils.utils import str_clean_up

KINGDOM, AUTH_KINGDOM, SOURCE_KINGDOM, SOURCE_ORIGIN_KINGDOM = "Kingdom", "kingdomAuthor", "kingdomSource", "kingdomOrigin"
PHYLUM, AUTH_PHYLUM, SOURCE_PHYLUM, SOURCE_ORIGIN_PHYLUM = "Phylum", "phylumAuthor", "phylumSource", "phylumOrigin"
CLASS, AUTH_CLASS, SOURCE_CLASS, SOURCE_ORIGIN_CLASS = "Class", "classAuthor", "classSource", "classOrigin"
ORDER, AUTH_ORDER, SOURCE_ORDER, SOURCE_ORIGIN_ORDER = "Order", "orderAuthor", "orderSource", "orderOrigin"
FAM, AUTH_FAM, SOURCE_FAM, SOURCE_ORIGIN_FAM = "Family", "familyAuthor", "familySource", "familyOrigin"
GENUS, AUTH_GENUS, SOURCE_GENUS, SOURCE_ORIGIN_GENUS = "Genus", "genusAuthor", "genusSource", "genusOrigin"
SPECIES, AUTH_SPECIES, SOURCE_SPECIES, SOURCE_ORIGIN_SPECIES = "Species", "speciesAuthor", "speciesSource", "speciesOrigin"
SUBSPECIES, AUTH_SUBSPECIES, SOURCE_SUBSPECIES, SOURCE_ORIGIN_SUBSPECIES = (
	"Subspecies",
	"subspeciesAuthor",
	"subspeciesSource",
	"subspeciesOrigin",
)
VARIETY, AUTH_VARIETY, SOURCE_VARIETY, SOURCE_ORIGIN_VARIETY = "Variety", "varietyAuthor", "varietySource", "varietyOrigin"
TAXON_RANK = "taxonRank"
ORIGINAL_NAME = "originalName"
ORIGINAL_STATUS = "originalStatus"
COL_NAME_ACCEPTED = "colNamesAccepted"
COL_ID = "colID"

LEVELS = [KINGDOM, PHYLUM, CLASS, ORDER, FAM, GENUS, SPECIES, SUBSPECIES, VARIETY]

LEVELS_PARAMS = {
	KINGDOM: [TaxonomicLevel.KINGDOM, AUTH_KINGDOM, SOURCE_KINGDOM, SOURCE_ORIGIN_KINGDOM],
	PHYLUM: [TaxonomicLevel.PHYLUM, AUTH_PHYLUM, SOURCE_PHYLUM, SOURCE_ORIGIN_PHYLUM],
	CLASS: [TaxonomicLevel.CLASS, AUTH_CLASS, SOURCE_CLASS, SOURCE_ORIGIN_CLASS],
	ORDER: [TaxonomicLevel.ORDER, AUTH_ORDER, SOURCE_ORDER, SOURCE_ORIGIN_ORDER],
	FAM: [TaxonomicLevel.FAMILY, AUTH_FAM, SOURCE_FAM, SOURCE_ORIGIN_FAM],
	GENUS: [TaxonomicLevel.GENUS, AUTH_GENUS, SOURCE_GENUS, SOURCE_ORIGIN_GENUS],
	SPECIES: [TaxonomicLevel.SPECIES, AUTH_SPECIES, SOURCE_SPECIES, SOURCE_ORIGIN_SPECIES],
	SUBSPECIES: [TaxonomicLevel.SUBSPECIES, AUTH_SUBSPECIES, SOURCE_SUBSPECIES, SOURCE_ORIGIN_SUBSPECIES],
	VARIETY: [TaxonomicLevel.VARIETY, AUTH_VARIETY, SOURCE_VARIETY, SOURCE_ORIGIN_VARIETY],
}


@transaction.atomic
def create_taxonomic_level(line, parent, batch, idx_name, rank, idx_author, idx_source, idx_source_origin):
	if idx_name == VARIETY and idx_name not in line:
		return parent
	if not line[idx_name]:
		return parent
	source = get_or_create_source(line, idx_source, idx_source_origin)
	verb_auth, auths, parsed_year = get_or_create_authorship(line, idx_author, batch, source)

	if TaxonomicLevel.TRANSLATE_RANK[line[TAXON_RANK]] == rank:
		accepted_modifier = None
		if "accepted" in line[ORIGINAL_STATUS]:
			accepted = True
			if TaxonomicLevel.ACCEPTED_MODIFIERS_TRANSLATE[TaxonomicLevel.PROVISIONAL] in line[ORIGINAL_STATUS]:
				accepted_modifier = TaxonomicLevel.PROVISIONAL
		elif "synonym" in line[ORIGINAL_STATUS]:
			accepted = False
			if TaxonomicLevel.ACCEPTED_MODIFIERS_TRANSLATE[TaxonomicLevel.AMBIGUOUS] in line[ORIGINAL_STATUS]:
				accepted_modifier = TaxonomicLevel.AMBIGUOUS
		elif TaxonomicLevel.ACCEPTED_MODIFIERS_TRANSLATE[TaxonomicLevel.MISAPPLIED] in line[ORIGINAL_STATUS]:
			accepted = False
			accepted_modifier = TaxonomicLevel.MISAPPLIED
		else:
			raise Exception(
				f'{ORIGINAL_STATUS} must be either "accepted", "misapplied" or "synonym" but was "{line[ORIGINAL_STATUS]}"\n{line}'
			)

		if line[idx_name][0].isupper() and rank in [TaxonomicLevel.SPECIES, TaxonomicLevel.SUBSPECIES, TaxonomicLevel.VARIETY]:
			raise Exception(f"Epithet cant be upper cased.\n{line}")

		child, new_taxon = TaxonomicLevel.objects.get_or_create(
			parent=parent,
			rank=rank,
			name__iexact=line[idx_name],
			defaults={
				"name": line[idx_name],
				"accepted": accepted,
				"accepted_modifier": accepted_modifier,
				"verbatim_authorship": verb_auth,
				"parsed_year": parsed_year,
				"batch": batch,
			},
		)

		os, new_source = OriginSource.objects.get_or_create(origin_id=line[COL_ID], source=source)
		if new_source:
			if child.sources.filter(source=os.source, origin_id=os.origin_id).exists():
				raise Exception(f"Origin source id already existing. {os}\n{line}")
			child.sources.add(os)
			child.save()
		elif not child.sources.filter(id=os.id).exists():
			raise Exception(f"Origin source id already existing. {os}\n{line}")

		if auths:
			child.authorship.add(*auths)
			child.save()

		if child.accepted != accepted or child.accepted_modifier != accepted_modifier:
			raise Exception(f"Trying to change taxonomy level status. {child.readable_rank()}:{child.name}\n{line}")

		if not accepted:
			accepted_candidates = TaxonomicLevel.objects.find(taxon=line[COL_NAME_ACCEPTED])
			candidates_count = accepted_candidates.count()
			if candidates_count == 0:
				raise Exception(f"No candidates found for synonyms linking\n{line}")
			if accepted_candidates.count() != 1:
				raise Exception(f"More than one potential candidates found for synonyms linking\n{line}")
			accepted_tl = accepted_candidates.first()

			if not accepted_tl:
				raise Exception(
					f"{parent} {rank} Accepted taxonomic level not found for {line[COL_NAME_ACCEPTED]}. Accepted taxon must be inserted first.\n{line}"
				)

			accepted_tl.synonyms.add(child)
			accepted_tl.save()
	else:
		child = TaxonomicLevel.objects.filter(parent=parent, rank=rank, name__iexact=line[idx_name])

		if child.count() == 0:
			raise Exception(
				f"Higher taxonomy must exist before loading a new taxon parent={parent} rank={TaxonomicLevel.TRANSLATE_RANK[rank]} name={line[idx_name]}\n{line}"
			)
		elif child.count() > 1:
			raise Exception(f"Found {child.count()} possible parent nodes {child} when loading a new taxon\n{line}")

		child = child.first()

		if not child.accepted and "synonym" not in line[ORIGINAL_STATUS]:
			raise Exception(f"Higher taxonomy must be accepted {child.readable_rank()}:{child.name}\n{line}")
		if child.verbatim_authorship != verb_auth or set(auths) != set(child.authorship.all() if child.authorship else []):
			raise Exception(
				f'Trying to update higher taxonomy author for {child.readable_rank()}:{child.name}. Verbatim: {child.verbatim_authorship} Original: {verb_auth}. Inferred: {child.authorship or "None"} New inferred: {auths or "None"}\n{line}'
			)

	return child


def parse_verbatim_authorship(input_string):
	input_string = re.sub(r"\(([^0-9|()]+)\),?", r"\1,", input_string)
	input_string = re.sub(r"\s*\(([0-9]+)\)", r", \1", input_string)
	input_string = re.sub(r"[()]", r"", input_string)

	years = re.findall(r"[^0-9]*(\d+)[^0-9]*", input_string)

	# if len(years) > 1:
	# 	raise Exception(f"Authorship must have only one year. Original: {input_string}, year: {years}")

	years = [int(year) for year in years]
	years.sort()

	if years:
		authors = re.findall(r"(.+),[^0-9]*\d+[^0-9]*", input_string)
	else:
		authors = [input_string]

	if len(authors) != 1:
		raise Exception(f"Authorship must have only one author string. Original: {input_string}, authors: {authors}")

	return authors[0] if authors else None, years[-1] if years else None


def get_or_create_authorship(line, idx_author, batch, source):
	if not line[idx_author]:
		return None, [], None

	parsed_name, parsed_year = parse_verbatim_authorship(line[idx_author])
	auths = []
	if parsed_name:
		parsed_authors = re.split(r"\s*[,;&]\s*|\s+[eE][xXtT]\s+", parsed_name)
		for pauthor in parsed_authors:
			if pauthor:
				auth, _ = Authorship.objects.get_or_create(
					name__iexact=pauthor,
					defaults={
						"name": pauthor,
						"accepted": True,
						"batch": batch,
					},
				)
				auths.append(auth)

	return line[idx_author], auths, parsed_year


def get_or_create_source(line, idx_source, idx_source_origin):
	if not line[idx_source]:
		raise Exception(f"All records must have a source\n{line}")

	source, _ = Source.objects.get_or_create(
		name__iexact=line[idx_source],
		data_type=Source.TAXON,  # Filter out 2 sources with the same name and data_type
		defaults={
			"name": line[idx_source],
			"accepted": True,
			"origin": Source.TRANSLATE_CHOICES[line[idx_source_origin]],
			"data_type": Source.TAXON,
			"url": None,
		},
	)

	return source


def clean_up_input_line(line):
	for key in line.keys():
		line[key] = str_clean_up(line[key])


class Command(BaseCommand):
	help = "Loads from taxonomy from csv"

	def add_arguments(self, parser):
		parser.add_argument("file", type=str)
		parser.add_argument("-d", nargs="?", type=str, default=";")

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		delimiter = options["d"]
		exception = False
		with TaxonomicLevel.objects.delay_mptt_updates():
			with open(file_name, encoding="windows-1252") as file:
				csv_file = csv.DictReader(file, delimiter=delimiter)
				batch = Batch.objects.create()
				biota, _ = TaxonomicLevel.objects.get_or_create(
					name__iexact="Biota",
					rank=TaxonomicLevel.LIFE,
					defaults={
						"name": "Biota",
						"accepted": True,
						"batch": batch,
						"parent": None,
					},
				)

				for line in csv_file:
					parent = biota
					clean_up_input_line(line)

					try:
						for level in LEVELS:
							parent = create_taxonomic_level(line, parent, batch, level, *LEVELS_PARAMS[level])
					except:
						exception = True
						print(traceback.format_exc())

				if exception:
					raise Exception("Errors found: Rollback control")
