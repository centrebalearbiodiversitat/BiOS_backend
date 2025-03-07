import csv
from django.core.management.base import BaseCommand
from apps.versioning.models import Source, Basis, Batch

from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
	help = "Load data into the Source model from a CSV file."

	def add_arguments(self, parser):
		parser.add_argument("csv_file", type=str, help="Path to the CSV file")

	def handle(self, *args, **options):
		csv_file = options["csv_file"]

		batch = Batch.objects.create()

		with open(csv_file, "r") as file:
			reader = csv.DictReader(file, delimiter=";")
			for row in reader:
				try:
					internal_name = row["internal_name"].lower()
					print(f"Buscando Basis con internal_name: {internal_name}")  # add this line
					basis = Basis.objects.get(
						internal_name__iexact=internal_name,
					)

					source, _ = Source.objects.get_or_create(
						source_type=Source.DATABASE,
						extraction_method=Source.API,
						data_type=Source.TRANSLATE_DATA_TYPE[row["data_type"]],
						url=row["url"],
						basis=basis,
						defaults={
							"batch": batch,
						},
					)
					if _:
						self.stdout.write(self.style.SUCCESS(f'Created Source "{source}"'))
				except ObjectDoesNotExist:
					self.stdout.write(self.style.ERROR(f"Basis matching query does not exist for internal_name: {internal_name} and row: {row}"))
				except Exception as e:
					self.stdout.write(self.style.ERROR(f"Error processing row: {row} - {e}"))
