from django.db.models import Subquery, OuterRef
from django.db.models.functions import Coalesce

from apps.taxonomy.models import TaxonomicLevel


def map_taxa_to_rank(ranks, taxa, authors=True):
	taxa_iter = iter(taxa)

	mapped_taxa = []
	current = next(taxa_iter, None)
	current_name = ""
	for rank in ranks:
		if current is None:
			break

		if rank == current.rank:
			if current.rank in [TaxonomicLevel.SPECIES, TaxonomicLevel.SUBSPECIES, TaxonomicLevel.VARIETY]:
				current_name = f"{current_name} {current.name}"
			else:
				current_name = current.name

			mapped_taxa.append(current_name)
			if authors:
				mapped_taxa.append(current.verbatim_authorship)
			current = next(taxa_iter, None)
		else:
			mapped_taxa.append(None)
			if authors:
				mapped_taxa.append(None)

	return mapped_taxa


class ObjectTaxon(object):
	pass


def generate_csv_taxon_list2(checklist):
	checklist_ids = {t.id for t in checklist}

	return taxon_checklist_to_csv(TaxonomicLevel.objects.get(id=1), checklist_ids)


def generate_csv_taxon_list(checklist):
	ranks = [rank[1].lower() for rank in TaxonomicLevel.RANK_CHOICES[:4]]
	ranks_map = [rank[0] for rank in TaxonomicLevel.RANK_CHOICES[:4]]
	to_csv = [
		[
			"id",
			"taxon",
			"status",
			"taxonRank",
			*ranks,
		]
	]

	subqueries = {}
	for rank, key in TaxonomicLevel.RANK_CHOICES[:4]:
		subqueries[key.lower()] = Coalesce(Subquery(TaxonomicLevel.objects.filter(lft__lte=OuterRef("lft"), rght__gte=OuterRef("rght"), rank=rank).values("name")[:1]), None)

	checklist = checklist.annotate(**subqueries)

	current_taxon = []
	for taxon in checklist:
		current_taxon.append(taxon)

		taxon_map = []
		for rank in ranks:
			obj = ObjectTaxon()
			obj.name = getattr(taxon, rank)
			obj.rank = TaxonomicLevel.TRANSLATE_RANK[rank]
			obj.verbatim_authorship = None
			if obj.name != None:
				taxon_map.append(obj)

		taxa_map = map_taxa_to_rank(ranks_map, taxon_map, authors=False)

		to_csv.append(
			[
				taxon.id,
				taxon.scientific_name(),
				taxon.readable_status(),
				taxon.readable_rank(),
				*taxa_map,
			]
		)

	return to_csv


def taxon_checklist_to_csv(head, ids: set = None):
	if ids is None:
		ids = set()
	ranks = [rank[1] for rank in TaxonomicLevel.RANK_CHOICES]
	ranks_map = [rank[0] for rank in TaxonomicLevel.RANK_CHOICES]
	to_csv = [
		[
			"id",
			"taxon",
			"status",
			"taxonRank",
			*list(sum([(f"{rank.lower()}", f"authorship{rank}") for rank in ranks], ())),
		]
	]

	upper_taxon = head.get_ancestors(include_self=False)  # .exclude(name__iexact='Biota')
	upper_taxon = list(upper_taxon)
	checklist = head.get_descendants(include_self=True)

	current_taxon = []
	last_level = -1
	for taxon in checklist:
		if last_level >= taxon.level:
			current_taxon = current_taxon[: len(current_taxon) - (last_level - taxon.level + 1)]

		current_taxon.append(taxon)
		if taxon.id in ids:
			taxa_map = map_taxa_to_rank(ranks_map, upper_taxon + current_taxon)
			to_csv.append([taxon.id, taxa_map[-2], taxon.readable_status(), taxon.readable_rank(), *taxa_map])
		last_level = taxon.level

	return to_csv
