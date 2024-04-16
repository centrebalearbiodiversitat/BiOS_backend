import csv

from django.core.management.base import BaseCommand
from django.db import transaction, models

from apps.taxonomy.models import Authorship, TaxonomicLevel
from apps.versioning.models import Batch, Source

KINGDOM, AUTH_KINGDOM, SOURCE_KINGDOM, SOURCE_ORIGIN_KINGDOM = 'Kingdom', 'kingdomAuthor', 'kingdomSource', 'kingdomOrigin'
PHYLUM, AUTH_PHYLUM, SOURCE_PHYLUM, SOURCE_ORIGIN_PHYLUM = 'Phylum', 'phylumAuthor', 'phylumSource', 'phylumOrigin'
CLASS, AUTH_CLASS, SOURCE_CLASS, SOURCE_ORIGIN_CLASS = 'Class', 'classAuthor', 'classSource', 'classOrigin'
ORDER, AUTH_ORDER, SOURCE_ORDER, SOURCE_ORIGIN_ORDER = 'Order', 'orderAuthor', 'orderSource', 'orderOrigin'
FAM, AUTH_FAM, SOURCE_FAM, SOURCE_ORIGIN_FAM = 'Family', 'familyAuthor', 'familySource', 'familyOrigin'
GENUS, AUTH_GENUS, SOURCE_GENUS, SOURCE_ORIGIN_GENUS = 'Genus', 'genusAuthor', 'genusSource', 'genusOrigin'
SPECIES, AUTH_SPECIES, SOURCE_SPECIES, SOURCE_ORIGIN_SPECIES = 'Species', 'speciesAuthor', 'speciesSource', 'speciesOrigin'
SUBSPECIES, AUTH_SUBSPECIES, SOURCE_SUBSPECIES, SOURCE_ORIGIN_SUBSPECIES = 'Subspecies', 'subspeciesAuthor', 'subspeciesSource', 'subspeciesOrigin'
VARIETY, AUTH_VARIETY, SOURCE_VARIETY, SOURCE_ORIGIN_VARIETY = 'Variety', 'varietyAuthor', 'varietySource', 'varietyOrigin'
TAXON_RANK = 'taxonRank'
ORIGINAL_NAME = 'originalName'
ORIGINAL_STATUS = 'originalStatus'
COL_NAME_ACCEPTED = 'colNamesAccepted'

LEVELS = [KINGDOM, PHYLUM, CLASS, ORDER, FAM, GENUS, SPECIES, SUBSPECIES]
# LEVELS = [KINGDOM, PHYLUM, CLASS, ORDER, FAM, GENUS, SPECIES, SUBSPECIES, VARIETY]

LEVELS_PARAMS = {
	KINGDOM: [TaxonomicLevel.KINGDOM, AUTH_KINGDOM, SOURCE_KINGDOM, SOURCE_ORIGIN_KINGDOM],
	PHYLUM: [TaxonomicLevel.PHYLUM, AUTH_PHYLUM, SOURCE_PHYLUM, SOURCE_ORIGIN_PHYLUM],
	CLASS: [TaxonomicLevel.CLASS, AUTH_CLASS, SOURCE_CLASS, SOURCE_ORIGIN_CLASS],
	ORDER: [TaxonomicLevel.ORDER, AUTH_ORDER, SOURCE_ORDER, SOURCE_ORIGIN_ORDER],
	FAM: [TaxonomicLevel.FAMILY, AUTH_FAM, SOURCE_FAM, SOURCE_ORIGIN_FAM],
	GENUS: [TaxonomicLevel.GENUS, AUTH_GENUS, SOURCE_GENUS, SOURCE_ORIGIN_GENUS],
	SPECIES: [TaxonomicLevel.SPECIES, AUTH_SPECIES, SOURCE_SPECIES, SOURCE_ORIGIN_SPECIES],
	SUBSPECIES: [TaxonomicLevel.SUBSPECIES, AUTH_SUBSPECIES, SOURCE_SUBSPECIES, SOURCE_ORIGIN_SUBSPECIES],
	# VARIETY: [TaxonomicLevel.VARIETY, AUTH_VARIETY, SOURCE_VARIETY, SOURCE_ORIGIN_VARIETY]
}


def create_taxonomic_level(line, parent, batch, idx_name, rank, idx_author, idx_source, idx_source_origin):
	if not line[idx_name]:
		return parent

	auth = get_or_create_authorship(line, idx_author, batch)
	source = get_or_create_source(line, idx_source, idx_source_origin)

	if TaxonomicLevel.TRANSLATE_RANK[line[TAXON_RANK]] == rank:
		if line[ORIGINAL_STATUS] == 'accepted':
			accepted = True
		elif line[ORIGINAL_STATUS] == 'synonym':
			accepted = False
		else:
			raise Exception(f'{ORIGINAL_STATUS} must be either "accepted" or "synonym" but was "{line[ORIGINAL_STATUS]}"\n{line}')

		child, _ = TaxonomicLevel.objects.get_or_create(
			parent=parent,
			rank=rank,
			name__iexact=line[idx_name],
			defaults={
				'name': line[idx_name],
				'accepted': accepted,
				'authorship': auth,
			}
		)

		if child.accepted != accepted:
			raise Exception(f'Trying to change taxonomy level status. {child.readable_rank()}:{child.name}')

		if not accepted:
			accepted_candidates = TaxonomicLevel.objects.find(taxon=line[COL_NAME_ACCEPTED])
			accepted_tl = None

			for candidate in accepted_candidates:
				if candidate.parent == parent and candidate.rank == rank:
					accepted_tl = candidate
					break

			if not accepted_tl:
				raise Exception(f'{parent} {rank} Accepted taxonomic level not found for {line[COL_NAME_ACCEPTED]}. Accepted taxon must be inserted first.')

			accepted_tl.synonyms.add(child)
			accepted_tl.save()
	else:
		child = TaxonomicLevel.objects.filter(
			parent=parent,
			rank=rank,
			name__iexact=line[idx_name]
		)

		if child.count() == 0:
			raise Exception(f'Higher taxonomy must exist before loading a new taxon parent={parent} rank={TaxonomicLevel.TRANSLATE_RANK[rank]} name={line[idx_name]}.\n{line}')
		elif child.count() > 1:
			raise Exception(f'Found {child.count()} possible parent nodes {child} when loading a new taxon.\n{line}')

		child = child.first()
		if not child.accepted:
			raise Exception(f'Higher taxonomy must be accepted {child.readable_rank()}:{child.name}.\n{line}')
		elif child.authorship != auth:
			raise Exception(f'Trying to update higher taxonomy author for {child.readable_rank()}:{child.name}. Original: {child.auth.name} New: {auth.name}.\n{line}')

	child.sources.add(source)
	child.references.add(batch)
	child.save()

	return child


def get_or_create_authorship(line, idx_author, batch):
	if not line[idx_author]:
		return None

	auth, _ = Authorship.objects.get_or_create(name=line[idx_author], accepted=True)
	auth.references.add(batch)
	auth.save()

	return auth


def get_or_create_source(line, idx_source, idx_source_origin):
	if not line[idx_source]:
		raise Exception('All records must have a source')

	source, _ = Source.objects.get_or_create(
		name=line[idx_source],
		defaults={
			'origin': Source.TRANSLATE_CHOICES[line[idx_source_origin]]
		}
	)

	return source


class Command(BaseCommand):
	help = "Loads from taxonomy from csv"

	def add_arguments(self, parser):
		parser.add_argument("file", type=str)
		parser.add_argument("-d", nargs='?', type=str, default=';')

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options['file']
		delimiter = options['d']
		with open(file_name, encoding='utf-8') as file:
			csv_file = csv.DictReader(file, delimiter=delimiter)
			biota, _ = TaxonomicLevel.objects.get_or_create(
				name="Biota",
				rank=TaxonomicLevel.LIFE,
				defaults={
					'accepted': True,
					'authorship': None,
					'parent': None,
				}
			)
			batch = Batch.objects.create()
			for line in csv_file:
				parent = biota
				print(line[ORIGINAL_NAME])

				for level in LEVELS:
					parent = create_taxonomic_level(line, parent, batch, level, *LEVELS_PARAMS[level])
