from apps.taxonomy.models import Habitat
from django.core.management.base import BaseCommand


class Command(BaseCommand):
	help = "Loads taxon habitats from a predefined list"

	def populate_habitat(self):
		habitats = [
			"forest",
			"savanna",
			"shrubland",
			"grassland",
			"wetlands (inland)",
			"rocky areas (e.g., inland cliffs, mountain peaks)",
			"caves & subterranean habitats (non-aquatic)",
			"desert",
			"marine neritic",
			"marine oceanic",
			"marine deep ocean floor (benthic and demersal)",
			"marine intertidal",
			"marine coastal/supratidal",
			"artificial/terrestrial",
			"artificial/aquatic",
			"introduced vegetation",
			"other",
			"unknown",
		]
		for habitat in habitats:
			Habitat.objects.get_or_create(name=habitat)

	def handle(self, *args, **kwargs):
		self.populate_habitat()
