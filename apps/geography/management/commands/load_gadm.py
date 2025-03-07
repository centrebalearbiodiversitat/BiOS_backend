import geopandas as gpd
from django.contrib.gis.geos import Point, GEOSGeometry, MultiPolygon

from django.core.management.base import BaseCommand
from django.db import transaction
from shapely import Polygon, MultiPolygon

from apps.geography.models import GeographicLevel

LEVELS = [
	{"key": "AC", "synonyms": "VARNAME_1", "rank": GeographicLevel.AC},
	{"key": "ISLAND", "synonyms": "VARNAME_2", "rank": GeographicLevel.ISLAND},
	{"key": "MUNICIPALI", "synonyms": "VARNAME_3", "rank": GeographicLevel.MUNICIPALITY},
	{"key": "TOWN", "synonyms": "VARNAME_4", "rank": GeographicLevel.TOWN},
	{"key": "WATER_BODY_0", "rank": GeographicLevel.WATER_BODY},
	{"key": "WATER_BODY_1", "rank": GeographicLevel.WATER_BODY},
]


class Command(BaseCommand):
	help = "Loads geographic taxonomy from GPKG files"

	def add_arguments(self, parser):
		parser.add_argument("file", type=str)

	@transaction.atomic
	def handle(self, *args, **options):
		file_name = options["file"]
		db = gpd.read_file(file_name)
		levels = db.loc[:]

		for i in range(len(levels)):
			# print(levels.iloc[i])
			parent = None
			for level in LEVELS:
				if level["key"] in levels:
					# if 'synonyms' in level:
					# 	synonyms = levels[level['synonyms']].iloc[i]
					parent = self.load_geo_level(
						parent,
						levels[level["key"]].iloc[i],
						level["rank"],
						levels["CEN_LAT"].iloc[i],
						levels["CEN_LON"].iloc[i],
						levels["RADIUS_M"].iloc[i],
						levels["geometry"].iloc[i],
						GeographicLevel.TRANSLATE_RANK[levels["RANK"].iloc[i].lower()],
					)

	def load_geo_level(self, parent, name, rank, lat, lon, uncert, geometry, new_rank):
		name = str(name).strip()

		if not name:
			return parent

		if rank == new_rank:
			if isinstance(geometry, Polygon):
				geometry = MultiPolygon([geometry])

			geometry = GEOSGeometry(str(geometry))

			if geometry.num_points > 10000:
				geometry = geometry.simplify(0.001, preserve_topology=True)

			gl, _ = GeographicLevel.objects.get_or_create(
				parent=parent,
				name__iexact=name,
				defaults={
					"name": name,
					"location": Point(lon, lat),
					"area": geometry,
					"coordinate_uncertainty_in_meters": uncert,
					"accepted": True,
					"rank": rank,
				},
			)
		else:
			gl = GeographicLevel.objects.get(parent=parent, name__iexact=name, rank=rank)

		# if synonyms:
		# 	synonyms = synonyms.split('|')
		# 	for syn in synonyms:
		# 		print('\t', syn)
		# 		syn = syn.strip()
		# 		if syn and syn != name:
		# 			gl_syn, _ = GeographicLevel.objects.get_or_create(parent=parent, name=syn, defaults={'accepted': False, 'rank': rank})
		# 			gl.synonyms.add(gl_syn)

		return gl
