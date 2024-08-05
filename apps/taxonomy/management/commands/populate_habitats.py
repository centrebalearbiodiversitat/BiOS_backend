from django.core.management.base import BaseCommand

from apps.taxonomy.models import Habitat
from apps.versioning.models import Batch, OriginSource, Source

IUCN = "IUCN"


def get_or_create_source(name, origin):
	if not name:
		raise Exception("All records must have a source")

	source, _ = Source.objects.get_or_create(
		name__iexact=name,
		data_type=Source.TAXON,  # Filter out 2 sources with the same name and data_type
		defaults={
			"name": name,
			"accepted": True,
			"origin": Source.TRANSLATE_CHOICES[origin],
			"data_type": Source.TAXON,
			"url": None,
		},
	)
	return source


class Command(BaseCommand):
	help = "Loads taxon habitats with IDs from a predefined list"

	def populate_habitat(self, batch):
		habitat_data = [
			("forest", 1),
			("savanna", 2),
			("shrubland", 3),
			("grassland", 4),
			("wetlands (inland)", 5),
			("rocky areas (e.g., inland cliffs, mountain peaks)", 6),
			("caves & subterranean habitats (non-aquatic)", 7),
			("desert", 8),
			("marine neritic", 9),
			("marine oceanic", 10),
			("marine deep ocean floor (benthic and demersal)", 11),
			("marine intertidal", 12),
			("marine coastal/supratidal", 13),
			("artificial/terrestrial", 14),
			("artificial/aquatic", 15),
			("introduced vegetation", 16),
			("other", 17),
			("unknown", 18),
		]

		for name, id in habitat_data:
			source = get_or_create_source(IUCN, "database")
			habitat, created = Habitat.objects.get_or_create(
				name=name,
				defaults={"name": name, "batch": batch},
			)

			os, new_source = OriginSource.objects.get_or_create(source=source, origin_id=id)
			if new_source:
				if habitat.sources.filter(source=os.source, origin_id=os.origin_id).exists():
					raise Exception(f"Origin source id already existing. {os}\n{name}")
				habitat.sources.add(os)
				habitat.save()
			elif not habitat.sources.filter(id=os.id).exists():
				raise Exception(f"Origin source id already existing. {os}\n{name}")

	def handle(self, *args, **kwargs):
		batch = Batch.objects.create()

		self.populate_habitat(batch)
