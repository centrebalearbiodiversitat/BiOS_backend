import inspect

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse



class TestResultHandler(TestCase):
	LOADED_DATA = False

	@classmethod
	def setUpTestData(cls):
		super().setUpTestData()
		if not cls.LOADED_DATA:
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
			call_command("load_taxonomy", "fixtures/taxonomy/Amphibia.csv")
			call_command("load_occurrences", "fixtures/occurrences/Alytes_muletensis.csv")
			call_command(
				"load_occurrences",
				"fixtures/genetics/Alytes_muletensis.csv",
			)
			call_command("populate_habitats")
			call_command(
				"load_taxon_data",
				"fixtures/NO_BORRAR/iucn/Amphibia_IUCN_2024_07_30.json"
			)
			cls.LOADED_DATA = True

	def assert_and_log(self, assertion_function, *args, **kwargs):
		current_function_name = inspect.stack()[1].function
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
