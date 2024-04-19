import re
import string

from django.db import models
from unidecode import unidecode

from common.utils.models import ReferencedModel, SynonymModel, LatLonModel, SynonymManager

PUNCTUATION_TRANSLATE = str.maketrans(string.punctuation, ' ' * len(string.punctuation))


class GeographicLevelManager(SynonymManager):
	def search(self, location: str):
		# Clean up location string for optimal search
		global PUNCTUATION_TRANSLATE
		location = location.translate(PUNCTUATION_TRANSLATE)

		loc_nodes = unidecode(location).split()

		potential_nodes = {}
		for node in loc_nodes:
			if node:
				for gl in self.filter(name__icontains=node):
					potential_nodes[gl.id] = gl

		# Calculate their score by matching and return the best
		potential_nodes_score = []
		for potn in potential_nodes.values():
			score = 0
			current = potn
			while current.parent:
				if current.id in potential_nodes:
					score += 1
				current = current.parent
			potential_nodes_score.append({'score': score, 'obj': potn})

		if potential_nodes_score:
			return max(potential_nodes_score, key=lambda x: x['score'])
		else:
			return None


class GeographicLevel(ReferencedModel, SynonymModel, LatLonModel):
	objects = GeographicLevelManager()

	AC = 2
	ISLAND = 3
	MUNICIPALITY = 4
	TOWN = 5
	WATER_BODY = 6

	RANK_CHOICES = (
		(AC, 'Autonomous community'),
		(ISLAND, 'Island'),
		(MUNICIPALITY, 'Municipality'),
		(TOWN, 'Town'),
		(WATER_BODY, 'Water body'),
	)

	TRANSLATE_RANK = {
		AC: 'autonomous_community',
		'autonomous_community': AC,
		ISLAND: 'island',
		'island': ISLAND,
		MUNICIPALITY: 'municipality',
		'municipality': MUNICIPALITY,
		TOWN: 'town',
		'town': TOWN,
		WATER_BODY: 'waterBody',
		'water_body': WATER_BODY,
	}

	rank = models.PositiveSmallIntegerField(choices=RANK_CHOICES)
	parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None, blank=True, related_name='children')

	class Meta:
		unique_together = ('parent', 'name')
		ordering = ['id']
