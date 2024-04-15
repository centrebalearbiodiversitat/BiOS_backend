from django.db import models

from apps.synonyms.models import ModelWithSynonyms
from apps.versioning.models import ModelWithReferences


class GeographicLevel(ModelWithReferences, ModelWithSynonyms):
	CONTINENT = 0
	COUNTRY = 1
	STATE_PROVINCE = 2
	COUNTY = 3
	MUNICIPALITY = 4
	LOCALITY = 5
	WATER_BODY = 6

	RANK_CHOICES = (
		(CONTINENT, 'Continent'),
		(COUNTRY, 'Country'),
		(STATE_PROVINCE, 'State province'),
		(COUNTY, 'County'),
		(MUNICIPALITY, 'Municipality'),
		(LOCALITY, 'Locality'),
		(WATER_BODY, 'Water body'),
	)

	TRANSLATE_RANK = {
		CONTINENT: 'continent',
		'continent': CONTINENT,
		COUNTRY: 'country',
		'country': COUNTRY,
		STATE_PROVINCE: 'stateProvince',
		'state_province': STATE_PROVINCE,
		COUNTY: 'county',
		'county': COUNTY,
		'municipality': MUNICIPALITY,
		LOCALITY: 'locality',
		'locality': LOCALITY,
		WATER_BODY: 'waterBody',
		'water_body': WATER_BODY,
	}

	rank = models.PositiveSmallIntegerField(choices=RANK_CHOICES)
	gid = models.CharField(max_length=256)
	parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None, blank=True, related_name='children')

	def __str__(self):
		return self.name

	class Meta:
		unique_together = ('parent', 'gid', 'name')
		ordering = ['id']
