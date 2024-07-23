import re
import string

from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from unidecode import unidecode

from common.utils.models import ReferencedModel, SynonymModel, LatLonModel, SynonymManager
from common.utils.utils import str_clean_up

PUNCTUATION_TRANSLATE = str.maketrans(string.punctuation, "\n" * len(string.punctuation))


class GeographicLevelManager(SynonymManager):
	def search(self, location: str):
		## First try by unique name query
		potential_nodes = self.filter(name__iexact=location)
		if potential_nodes.count() > 1:
			return potential_nodes.first()

		## Second try by higher taxonomy
		# Clean up location string for optimal search
		global PUNCTUATION_TRANSLATE
		location = location.translate(PUNCTUATION_TRANSLATE)
		loc_nodes = unidecode(location).split("\n")
		clean_loc_nodes = []

		# Query potential nodes with the exact name
		best_node = None
		for node in loc_nodes:
			node = str_clean_up(node)
			potential_node = self.filter(name__iexact=node)
			if potential_node.exists():
				if best_node:
					for pn in potential_node:
						if best_node.rank < pn.rank:
							best_node = pn
							break
				else:
					best_node = potential_node.first()  # most uncertainty

		return best_node


class GeographicLevel(SynonymModel, MPTTModel, LatLonModel):
	objects = GeographicLevelManager()

	DEFAULT_BALEARIC_ISLANDS_ID = 1

	# Order matters!
	AC = 2
	ISLAND = 3
	MUNICIPALITY = 4
	TOWN = 5
	WATER_BODY = 6

	RANK_CHOICES = (
		(AC, "Autonomous community"),
		(ISLAND, "Island"),
		(MUNICIPALITY, "Municipality"),
		(TOWN, "Town"),
		(WATER_BODY, "Water body"),
	)

	TRANSLATE_RANK = {
		AC: "ac",
		"ac": AC,
		ISLAND: "island",
		"island": ISLAND,
		MUNICIPALITY: "municipality",
		"municipality": MUNICIPALITY,
		TOWN: "town",
		"town": TOWN,
		WATER_BODY: "waterBody",
		"wb_0": WATER_BODY,
	}

	rank = models.PositiveSmallIntegerField(choices=RANK_CHOICES)
	parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, default=None, blank=True)

	def get_readable_rank(self):
		return GeographicLevel.TRANSLATE_RANK[self.rank]

	class Meta:
		unique_together = ("parent", "name")
		ordering = ["rank"]
