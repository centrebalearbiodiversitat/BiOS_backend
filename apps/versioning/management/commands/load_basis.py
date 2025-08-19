import json
import traceback

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.versioning.models import Batch, Basis
from common.utils.utils import is_batch_referenced


def populate_basis(line, batch):
	Basis.objects.update_or_create(
		internal_name__iexact=line.get("internal_name", ""),
		type=Basis.TRANSLATE_TYPE[line["type"]],
		defaults={
			"internal_name": line.get("internal_name", None),
			"name": line["name"],
			"type": Basis.TRANSLATE_TYPE[line["type"]],
			"acronym": line.get("acronym", None),
			"url": line.get("url", None),
			"description": line.get("description", None),
			"citation": line.get("citation", None),
			"contact": line.get("contact", None),
			"authors": line.get("authors", None),
			"image": line.get("image", None),
			"batch": batch,
		},
	)


class Command(BaseCommand):
	help = "Populates the Source table with data from a JSON file."

	def add_arguments(self, parser):
		parser.add_argument("json_file", type=str, help="Path to the JSON file containing source data.")

	@transaction.atomic
	def handle(self, *args, **options):
		json_file = options["json_file"]

		with open(json_file, "r") as f:
			json_file = json.load(f)
			batch = Batch.objects.create()

		try:
			for line in json_file:
				populate_basis(line, batch)
		except Exception as e:
			print(traceback.format_exc())
			raise e

		is_batch_referenced(batch)
