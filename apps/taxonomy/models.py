import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Substr, Lower, Upper
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel, TreeManager
from apps.versioning.models import Batch, OriginSource
from common.utils.models import ReferencedModel, SynonymManager, SynonymModel
from common.utils.utils import str_clean_up


class Authorship(SynonymModel):
	batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, default=None)


class TaxonomicLevelManager(SynonymManager, TreeManager):
	def get_queryset(self):
		qs = super().get_queryset()

		return qs.prefetch_related(
			models.Prefetch("parent__parent", to_attr="parent__parent"),
		)

	def find(self, taxon):
		# regex for properly split handle when hybrids or
		# 	hyphen "-" (eg. Allium antonii-bolosii)
		levels = re.findall(r"\bx\s+[\w|-]+|[\w|-]+", taxon)
		if len(levels) < 1:
			return self.none()

		query = self.filter(name__iexact=levels[0])
		for level in levels[1:]:
			query = self.filter(parent__in=query, name__iexact=level)

		return query

	def contains(self, taxon):
		levels: list = taxon.split()
		assert len(levels) > 0, []

		query = self.none()
		for level in levels:
			query |= self.filter(name__icontains=level)

		return query


class TaxonomicLevel(SynonymModel, MPTTModel, ReferencedModel):
	objects = TaxonomicLevelManager()

	KINGDOM = 0
	PHYLUM = 1
	CLASS = 2
	ORDER = 3
	FAMILY = 4
	GENUS = 5
	SPECIES = 6
	SUBSPECIES = 7
	VARIETY = 8
	LIFE = 9

	# !Order matters!
	RANK_CHOICES = (
		(LIFE, "Life"),
		(KINGDOM, "Kingdom"),
		(PHYLUM, "Phylum"),
		(CLASS, "Class"),
		(ORDER, "Order"),
		(FAMILY, "Family"),
		(GENUS, "Genus"),
		(SPECIES, "Species"),
		(SUBSPECIES, "Subspecies"),
		(VARIETY, "Variety"),
	)
	TRANSLATE_RANK = {
		KINGDOM: "kingdom",
		"kingdom": KINGDOM,
		PHYLUM: "phylum",
		"phylum": PHYLUM,
		CLASS: "class",
		"class": CLASS,
		ORDER: "order",
		"order": ORDER,
		FAMILY: "family",
		"family": FAMILY,
		GENUS: "genus",
		"genus": GENUS,
		SPECIES: "species",
		"species": SPECIES,
		SUBSPECIES: "subspecies",
		"subspecies": SUBSPECIES,
		VARIETY: "variety",
		"variety": VARIETY,
		LIFE: "life",
		"life": LIFE,
	}

	rank = models.PositiveSmallIntegerField(choices=RANK_CHOICES)
	verbatim_authorship = models.CharField(max_length=256, null=True, default=None, blank=True)
	parsed_year = models.PositiveIntegerField(null=True, default=None, blank=True)
	authorship = models.ManyToManyField(Authorship, blank=True, symmetrical=False)
	parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, default=None, blank=True)
	images = models.ManyToManyField(OriginSource, blank=True, symmetrical=False, related_name="images_os")

	def clean(self):
		if self.verbatim_authorship:
			self.verbatim_authorship = str_clean_up(self.verbatim_authorship)
		return super().clean()

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		if self.rank == TaxonomicLevel.SPECIES and len(re.sub("^x ", "", self.name).split()) != 1:
			raise ValidationError(f"Species level must be epithet separated of genus.\n{self.name}")

		super().save(force_insert, force_update, using, update_fields)

	def __str__(self):
		return self.scientific_name()

	def readable_rank(self):
		return TaxonomicLevel.TRANSLATE_RANK[self.rank]

	def scientific_name(self):
		full_name = self.name
		if self.rank in [TaxonomicLevel.SPECIES, TaxonomicLevel.SUBSPECIES, TaxonomicLevel.VARIETY]:
			current = self
			while current.rank != TaxonomicLevel.GENUS:
				full_name = f"{current.parent.name} {full_name}"
				current = current.parent

		return full_name

	class Meta:
		unique_together = ("parent", "name", "rank")
		indexes = [
			models.Index(
				Lower(Substr("unidecode_name", 1, 1)),
				name="unidecode_name_l1_substr_idx",
			),
			models.Index(
				Lower(Substr("unidecode_name", 1, 2)),
				name="unidecode_name_l2_substr_idx",
			),
			models.Index(
				Lower(Substr("unidecode_name", 1, 3)),
				name="unidecode_name_l3_substr_idx",
			),
			models.Index(
				Upper("unidecode_name"),
				name="unidecode_name_insensitive",
			),
		]
		index_together = [
			("tree_id", "lft", "rght"),
			("tree_id", "rght"),
			("tree_id", "lft"),
			("rght", "lft"),
			("rght",),
			("lft",),
			("rank",),
		]

	class MPTTMeta:
		order_insertion_by = ["name"]