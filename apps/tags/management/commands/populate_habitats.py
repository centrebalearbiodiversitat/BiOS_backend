from django.core.management.base import BaseCommand
from django.db import transaction

from apps.tags.models import Habitat
from apps.versioning.models import Batch, OriginId
from common.utils.utils import get_or_create_module

API = "api"
DATABASE = "database"
IUCN = "IUCN"
TAXON = "taxon"

HABITATS = [
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


class Command(BaseCommand):
	help = "Loads taxon habitats with IDs from a predefined list"

	def populate_habitat(self, batch):
		for name, iucn_id in HABITATS:
			module = get_or_create_module(
				source_type=DATABASE,
				extraction_method=API,
				data_type=TAXON,
				batch=batch,
				internal_name=IUCN,
			)
			habitat, created = Habitat.objects.get_or_create(
				name=name,
				defaults={"name": name, "batch": batch},
			)

			os, new_source = OriginId.objects.get_or_create(module=module, external_id=iucn_id)
			if new_source:
				if habitat.sources.filter(module=os.module, external_id=os.external_id).exists():
					raise Exception(f"Origin source id already existing. {os}\n{name}")
				habitat.sources.add(os)
				habitat.save()
			elif not habitat.sources.filter(id=os.id).exists():
				raise Exception(f"Origin source id already existing. {os}\n{name}")
		self.stdout.write(self.style.SUCCESS(f"Successfully created habitats"))

	@transaction.atomic
	def handle(self, *args, **kwargs):
		self.populate_habitat(Batch.objects.create())
