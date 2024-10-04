import inspect

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse


class TestResultHandler(TestCase):
	@classmethod
	def setUpTestData(cls):
		super().setUpTestData()
		print("Loading fixtures...")
		call_command(
			"load_gadm",
			"fixtures/gadm/CA/CA_uncertainess.shp",
		)
		call_command(
			"load_gadm",
			"fixtures/gadm/island/island_uncertainess.shp",
		)
		call_command(
			"load_gadm",
			"fixtures/gadm/municipality/municipality_uncertainess.shp",
		)
		call_command(
			"load_gadm",
			"fixtures/gadm/poblaciones/poblaciones_uncertainess.shp",
		)
		call_command("load_taxonomy_new", "fixtures/taxonomy/new_Amphibia_cbbdatabase.csv")
		call_command("load_occurrences_new", "fixtures/occurrences/Alytes muletensis (Sanchíz & Adrover, 1979).json")
		# call_command(
		# 	"load_occurrences_new",
		# 	"fixtures/genetics/Alytes_muletensis.csv",
		# )
		# call_command("populate_habitats")
		# call_command("load_taxon_data", "fixtures/iucn/Amphibia.json")
		# print("Finished loading fixtures...")

	def assert_and_log(self, assertion_function, *args, **kwargs):
		# current_function_name = inspect.stack()[1].function
		try:
			assertion_function(*args, **kwargs)
		# print(f"\033[92m==> {current_function_name}: PASSED\033[0m")
		except AssertionError as e:
			# print(f"\033[91m{e}\033[0m")
			# print(f"\033[91m==> {current_function_name}: FAILED\033[0m")
			raise

	def kwargs_to_string(self, **kwargs):
		return "&".join([f"{key}={value}" for key, value in kwargs.items()])

	def _generate_url(self, reverse_name, **kwargs):
		return f"{reverse(reverse_name)}?{self.kwargs_to_string(**kwargs)}"
