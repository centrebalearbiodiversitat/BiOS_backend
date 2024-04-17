from django.db import models

from common.util.models import ReferencedModel, SynonymModel


class GeographicLevel(ReferencedModel, SynonymModel):
	CONTINENT = 0
	COUNTRY = 1
	AC = 2
	ISLAND = 3
	MUNICIPALITY = 4
	TOWN = 5
	WATER_BODY = 6

	RANK_CHOICES = (
		(CONTINENT, 'Continent'),
		(COUNTRY, 'Country'),
		(AC, 'Autonomous community'),
		(ISLAND, 'Island'),
		(MUNICIPALITY, 'Municipality'),
		(TOWN, 'Town'),
		(WATER_BODY, 'Water body'),
	)

	TRANSLATE_RANK = {
		CONTINENT: 'continent',
		'continent': CONTINENT,
		COUNTRY: 'country',
		'country': COUNTRY,
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

	def __str__(self):
		return self.name

	class Meta:
		unique_together = ('parent', 'name')
		ordering = ['id']
