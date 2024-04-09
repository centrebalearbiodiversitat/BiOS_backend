import geopandas as gpd

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.geography.models import GeographicLevel

LEVELS = [
	{'key': 'CONTINENT', 'gid': 'CONTINENT', 'rank': GeographicLevel.CONTINENT},
	{'key': 'NAME_0', 'gid': 'GID_0', 'rank': GeographicLevel.COUNTRY},
	{'key': 'NAME_1', 'gid': 'GID_1', 'rank': GeographicLevel.STATE_PROVINCE},
	{'key': 'NAME_2', 'gid': 'GID_2', 'rank': GeographicLevel.COUNTY},
	{'key': 'NAME_3', 'gid': 'GID_3', 'rank': GeographicLevel.MUNICIPALITY},
	{'key': 'NAME_4', 'gid': 'GID_4', 'rank': GeographicLevel.LOCALITY},
	{'key': 'WATER_BODY_0', 'gid': 'WBID_0', 'rank': GeographicLevel.WATER_BODY},
	{'key': 'WATER_BODY_1', 'gid': 'WBID_1', 'rank': GeographicLevel.WATER_BODY},
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
		levels = db.loc[:, db.columns.isin([
			'CONTINENT',
			'NAME_0', 'GID_0',
			'NAME_1', 'GID_1',
			'NAME_2', 'GID_2',
			'NAME_3', 'GID_3',
			'NAME_4', 'GID_4']
		)]

		# parent = GeographicLevel.objects.get_or_create(name='Earth', gid="EARTH", accepted=True, rank=)
		for i in range(len(levels)):
			parent = None
			for level in LEVELS:
				if level['key'] in levels:
					parent = self.load_geo_level(parent, levels[level['key']].iloc[i], levels[level['gid']].iloc[i], level['rank'])

	def load_geo_level(self, parent, name, gid, rank):
		gl, _ = GeographicLevel.objects.get_or_create(gid=gid, parent=parent, defaults={'name': name, 'accepted': True, 'rank': rank})
		print(gl.name)

		return gl