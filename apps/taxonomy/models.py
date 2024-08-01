import re

from django.core.exceptions import ValidationError
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from apps.versioning.models import Batch, OriginSource
from common.utils.models import ReferencedModel, SynonymModel, SynonymManager
from common.utils.utils import str_clean_up


class Authorship(SynonymModel):
	batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True, default=None)


class TaxonomicLevelManager(SynonymManager):
	def get_queryset(self):
		qs = super().get_queryset()

		return qs.prefetch_related(
			models.Prefetch("parent__parent", to_attr="parent__parent"),
			# models.Prefetch('parent__parent', queryset=self.all(), to_attr='parent__parent'),
			# models.Prefetch('parent', queryset=self.all(), to_attr='parent')
		)

	def find(self, taxon):
		levels: list = taxon.split()
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
			raise ValidationError("Species level must be epithet separated of genus.")

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
