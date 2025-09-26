import csv
import re
import sys
import traceback

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.taxonomy.models import Authorship, TaxonomicLevel
from apps.versioning.models import Batch, OriginId, Source, Basis
from common.utils.utils import str_clean_up, get_or_create_source, is_batch_referenced
from tqdm import tqdm

KINGDOM = "kingdom"
PHYLUM = "phylum"
CLASS = "class"
ORDER = "order"
FAMILY = "family"
GENUS = "genus"
SPECIES = "species"
SUBSPECIES = "subspecies"
VARIETY = "variety"

LEVELS = [KINGDOM, PHYLUM, CLASS, ORDER, FAMILY, GENUS, SPECIES, SUBSPECIES, VARIETY]

LEVELS_PARAMS = {
	KINGDOM: TaxonomicLevel.KINGDOM,
	PHYLUM: TaxonomicLevel.PHYLUM,
	CLASS: TaxonomicLevel.CLASS,
	ORDER: TaxonomicLevel.ORDER,
	FAMILY: TaxonomicLevel.FAMILY,
	GENUS: TaxonomicLevel.GENUS,
	SPECIES: TaxonomicLevel.SPECIES,
	SUBSPECIES: TaxonomicLevel.SUBSPECIES,
	VARIETY: TaxonomicLevel.VARIETY,
}

ACCEPTED_TAXON = "accepted_taxon"
AUTHOR_ACCEPTED = "author_accepted"
ORIGIN_TAXON = "origin_taxon"
RANK = "rank"
SOURCE = "source"
SOURCE_TYPE = "origin"
STATUS = "status"
TAXON_ID = "taxon_id"


def create_taxonomic_level(line, parent, batch, idx_name, rank):
	if idx_name == VARIETY and idx_name not in line:
		return parent
	if not line[idx_name]:
		return parent

	if TaxonomicLevel.TRANSLATE_RANK[line[RANK]] == rank:
		accepted_modifier = None
		if "accepted" in line[STATUS]:
			accepted = True
			if TaxonomicLevel.ACCEPTED_MODIFIERS_TRANSLATE[TaxonomicLevel.PROVISIONAL] in line[STATUS]:
				accepted_modifier = TaxonomicLevel.PROVISIONAL
		elif "synonym" in line[STATUS]:
			accepted = False
			if TaxonomicLevel.ACCEPTED_MODIFIERS_TRANSLATE[TaxonomicLevel.AMBIGUOUS] in line[STATUS]:
				accepted_modifier = TaxonomicLevel.AMBIGUOUS
		elif TaxonomicLevel.ACCEPTED_MODIFIERS_TRANSLATE[TaxonomicLevel.MISAPPLIED] in line[STATUS]:
			accepted = False
			accepted_modifier = TaxonomicLevel.MISAPPLIED
		else:
			raise Exception(
				f'{STATUS} must be either "accepted", "misapplied" or "synonym" but was "{line[STATUS]}"\n{line}'
			)

		if rank in {TaxonomicLevel.SPECIES, TaxonomicLevel.SUBSPECIES, TaxonomicLevel.VARIETY}:
			if line[ORIGIN_TAXON] != " ".join(
				filter(lambda x: x, [line[GENUS], line[SPECIES], line[SUBSPECIES], line[VARIETY]])
			):
				raise Exception(f"Taxonomy mismatch with accepted taxon name.\n{line}")
		elif line[ORIGIN_TAXON].split()[-1] != line[idx_name]:
			raise Exception(f"Taxonomy mismatch with accepted taxon name.\n{line}")

		if line[idx_name][0].isupper() and rank in [
			TaxonomicLevel.SPECIES,
			TaxonomicLevel.SUBSPECIES,
			TaxonomicLevel.VARIETY,
		]:
			raise Exception(f"Epithet cant be upper cased.\n{line}")

		source = get_or_create_source(
			source_type=line[SOURCE_TYPE],
			extraction_method=Source.API,
			data_type=Source.TAXON,
			batch=batch,
			internal_name=line[SOURCE],
		)
		verb_auth, auths, parsed_year = get_or_create_authorship(line, batch)

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

		os, new_source = OriginId.objects.get_or_create(
			external_id__iexact=line[TAXON_ID],
			source=source,
			defaults={
				"external_id": line[TAXON_ID],
			},
		)
		if new_source or os.taxonomiclevel_set.count() == 0:
			if child.sources.filter(source=os.source, external_id__iexact=os.external_id).exists():
				raise Exception(f"Origin ID already existing. {os}\n{line}")
			child.sources.add(os)
		elif not child.sources.filter(id=os.id).exists():
			raise Exception(f"Origin ID already existing. {os}\n{line}")

		if auths:
			child.authorship.add(*auths)

		if child.accepted != accepted or child.accepted_modifier != accepted_modifier:
			raise Exception(f"Trying to change taxonomy level status. {child.readable_rank()}:{child.name}\n{line}")

		if not accepted:
			accepted_candidates = TaxonomicLevel.objects.find(taxon=line[ACCEPTED_TAXON])
			candidates_count = accepted_candidates.count()
			if candidates_count == 0:
				raise Exception(f"No candidates found for synonyms linking\n{line}")
			if accepted_candidates.count() != 1:
				raise Exception(f"More than one potential candidates found for synonyms linking\n{line}")
			accepted_tl = accepted_candidates.first()

			if not accepted_tl:
				raise Exception(
					f"{parent} {rank} Accepted taxonomic level not found for {line[ACCEPTED_TAXON]}. Accepted taxon must be inserted first.\n{line}"
				)

			accepted_tl.synonyms.add(child)
	else:
		child = TaxonomicLevel.objects.filter(parent=parent, rank=rank, name__iexact=line[idx_name])

		if child.count() == 0:
			raise Exception(
				f"Higher taxonomy must exist before loading a new taxon parent={parent} rank={TaxonomicLevel.TRANSLATE_RANK[rank]} name={line[idx_name]}\n{line}"
			)
		elif child.count() > 1:
			raise Exception(f"Found {child.count()} possible parent nodes {child} when loading a new taxon\n{line}")

		child = child.first()

		if not child.accepted and "synonym" not in line[STATUS]:
			raise Exception(f"Higher taxonomy must be accepted {child.readable_rank()}:{child.name}\n{line}")

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


def get_or_create_authorship(line, batch):
	if not line[AUTHOR_ACCEPTED]:
		return None, [], None

	parsed_name, parsed_year = parse_verbatim_authorship(line[AUTHOR_ACCEPTED])
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

	return line[AUTHOR_ACCEPTED], auths, parsed_year


def clean_up_input_line(line):
	for key in line.keys():
		line[key] = str_clean_up(line[key])
		try:
			line[key] = line[key].encode("latin-1").decode("utf-8")
		except:
			pass


class Command(BaseCommand):
	help = "Loads taxonomy from csv"

	def add_arguments(self, parser):
		parser.add_argument("file", type=str)
		parser.add_argument("-d", nargs="?", type=str, default=";")

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		delimiter = options["d"]
		exception = False
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

			with TaxonomicLevel.objects.delay_mptt_updates():
				for line in tqdm(list(csv_file), ncols=50, colour="yellow", smoothing=0, miniters=100, delay=20):
					parent = biota
					clean_up_input_line(line)
					try:
						for level in LEVELS:
							parent = create_taxonomic_level(line, parent, batch, level, LEVELS_PARAMS[level])
					except:
						exception = True
						print(traceback.format_exc())

			if exception:
				raise Exception("Errors found: Rollback control")

			is_batch_referenced(batch)
