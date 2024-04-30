import geopandas as gpd

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.geography.models import GeographicLevel

LEVELS = [
	{'key': 'AC', 'synonyms': 'VARNAME_1', 'rank': GeographicLevel.AC},
	{'key': 'ISLAND', 'synonyms': 'VARNAME_2', 'rank': GeographicLevel.ISLAND},
	{'key': 'MUNICIPALI', 'synonyms': 'VARNAME_3', 'rank': GeographicLevel.MUNICIPALITY},
	{'key': 'TOWN', 'synonyms': 'VARNAME_4', 'rank': GeographicLevel.TOWN},
	{'key': 'WATER_BODY_0', 'rank': GeographicLevel.WATER_BODY},
	{'key': 'WATER_BODY_1', 'rank': GeographicLevel.WATER_BODY},
]


class Command(BaseCommand):
	help = "Loads geographic taxonomy from GPKG files"

	def add_arguments(self, parser):
		parser.add_argument("file", type=str)

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options['file']
		print(file_name)
		db = gpd.read_file(file_name)
		levels = db.loc[:]

		for i in range(len(levels)):
			parent = None
			for level in LEVELS:
				if level['key'] in levels:
					# if 'synonyms' in level:
					# 	synonyms = levels[level['synonyms']].iloc[i]
					parent = self.load_geo_level(parent, levels[level['key']].iloc[i], level['rank'], levels['CEN_LAT'].iloc[i], levels['CEN_LON'].iloc[i], levels['RADIUS_M'].iloc[i], GeographicLevel.TRANSLATE_RANK[levels['RANK'].iloc[i].lower()])

	def load_geo_level(self, parent, name, rank, lat, lon, uncert, new_rank):
		name = str(name).strip()

		if not name:
			return parent

		if rank == new_rank:
			gl, _ = GeographicLevel.objects.get_or_create(
				parent=parent,
				name__iexact=name,
				defaults={
					'name': name,
					'latitude': lat,
					'longitude': lon,
					'coordinatesUncertainty': uncert,
					'accepted': True,
					'rank': rank
				}
			)
		else:
			gl = GeographicLevel.objects.get(
				parent=parent,
				name__iexact=name,
				rank=rank
			)

		# if synonyms:
		# 	synonyms = synonyms.split('|')
		# 	for syn in synonyms:
		# 		print('\t', syn)
		# 		syn = syn.strip()
		# 		if syn and syn != name:
		# 			gl_syn, _ = GeographicLevel.objects.get_or_create(parent=parent, name=syn, defaults={'accepted': False, 'rank': rank})
		# 			gl.synonyms.add(gl_syn)

		return gl