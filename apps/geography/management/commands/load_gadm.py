import geopandas as gpd

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.geography.models import GeographicLevel

LEVELS = [
	{'key': 'CONTINENT', 'gid': 'CONTINENT', 'rank': GeographicLevel.CONTINENT},
	{'key': 'NAME_0', 'gid': 'GID_0', 'synonyms': 'VARNAME_0', 'rank': GeographicLevel.COUNTRY},
	{'key': 'NAME_1', 'gid': 'GID_1', 'synonyms': 'VARNAME_1', 'rank': GeographicLevel.STATE_PROVINCE},
	{'key': 'NAME_2', 'gid': 'GID_2', 'synonyms': 'VARNAME_2', 'rank': GeographicLevel.COUNTY},
	{'key': 'NAME_3', 'gid': 'GID_3', 'synonyms': 'VARNAME_3', 'rank': GeographicLevel.MUNICIPALITY},
	{'key': 'NAME_4', 'gid': 'GID_4', 'synonyms': 'VARNAME_4', 'rank': GeographicLevel.LOCALITY},
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
		levels = db.loc[:]

		# parent = GeographicLevel.objects.get_or_create(name='Earth', gid="EARTH", accepted=True, rank=)
		for i in range(len(levels)):
			parent = None
			for level in LEVELS:
				synonyms = None
				if level['key'] in levels:
					if 'synonyms' in level:
						synonyms = levels[level['synonyms']].iloc[i]
					parent = self.load_geo_level(parent, levels[level['key']].iloc[i], levels[level['gid']].iloc[i], level['rank'], synonyms)

	def load_geo_level(self, parent, name, gid, rank, synonyms):
		name = str(name).strip()
		gid = str(gid).strip()

		if not (name and gid):
			return parent

		print(name, gid)
		gl, _ = GeographicLevel.objects.get_or_create(gid=gid, parent=parent, name=name, defaults={'accepted': True, 'rank': rank})

		if synonyms:
			synonyms = synonyms.split('|')
			for syn in synonyms:
				print('\t', syn)
				syn = syn.strip()
				if syn and syn != name:
					gl_syn, _ = GeographicLevel.objects.get_or_create(gid=gid, parent=parent, name=syn, defaults={'accepted': False, 'rank': rank})
					gl.synonyms.add(gl_syn)

		return gl