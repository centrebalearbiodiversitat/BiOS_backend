import csv

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.versioning.models import Source
from tqdm import tqdm


class Command(BaseCommand):
	help = "Load data into the Source model from a CSV file."

	def add_arguments(self, parser):
		parser.add_argument("csv_file", type=str, help="Path to the CSV file")

	@transaction.atomic
	def handle(self, *args, **options):
		csv_file = options["csv_file"]
		with open(csv_file, "r", encoding="utf-8-sig") as file:
			reader = csv.DictReader(file, delimiter=";")
			for row in tqdm(reader, ncols=50, colour="yellow", smoothing=0, miniters=100, delay=20):
				internal_name = row["internal_name"]
				try:
					Source.objects.filter(
						basis__internal_name__iexact=internal_name,
						data_type=Source.TRANSLATE_DATA_TYPE[row["data_type"]],
					).update(url=row["url"])
				except Source.DoesNotExist:
					print(f"Source does not exist.\n{row}")
