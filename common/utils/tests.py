import inspect

from django.core.management import call_command
from django.test import TestCase


class TestResultHandler(TestCase):
	@classmethod
	def setUpTestData(cls):
		super().setUpTestData()

		call_command(
			"load_gadm",
			"data/NO_BORRAR/GIS/IDEIB_AC/Comunidad_autonoma_uncertainess/CA_uncertainess.shp",
		)
		call_command(
			"load_gadm",
			"data/NO_BORRAR/GIS/IDEIB_islands/island_uncertainess/island_uncertainess.shp",
		)
		call_command(
			"load_gadm",
			"data/NO_BORRAR/GIS/IDEIB_municipalities/municipality_uncertainess/municipality_uncertainess.shp",
		)
		call_command(
			"load_gadm",
			"data/NO_BORRAR/GIS/CNIG_poblaciones/CNIG_poblaciones_uncertainess/poblacione_uncertain.shp",
		)
		call_command("load_taxonomy", "data/NO_BORRAR/taxonomy/Amphibia_cbbdatabase.csv")
		call_command("load_occurrences", "data/NO_BORRAR/occurrences/Alytes_muletensis.csv")
		call_command(
			"load_occurrences",
			"data/NO_BORRAR/genetics/Alytes_muletensis_2024-07-10.csv",
		)
		call_command("populate_habitats")
		call_command("load_taxon_data", "data/NO_BORRAR/iucn/Amphibia_IUCN_2024_07_30.json")

	def assert_and_log(self, assertion_function, *args, **kwargs):
		current_function_name = inspect.stack()[1].function
		try:
			assertion_function(*args, **kwargs)
			print(f"\033[92m=) {current_function_name}: PASSED\033[0m")
		except AssertionError:
			print(f"\033[91m=( {current_function_name}: FAILED\033[0m")
			raise
