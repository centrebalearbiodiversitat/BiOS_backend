import json
import re
import traceback

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.taxonomy.models import Authorship
from apps.versioning.models import Batch, Basis

def get_or_create_authorship(author, batch):
		if not author:
			return None, [], None
		auths = []
		if author:
			pauthors = re.split(r"\s*[,;&]\s*|\s+[eE][xXtT]\s+", author)
			for pauthor in pauthors:
				if pauthor:
					auth, _ = Authorship.objects.get_or_create(
						name__iexact=pauthor,
						defaults={
							"name": pauthor,
							"accepted": True,
							"batch": batch,
						},
					)
					auths.append(auth)
		return auths

def populate_basis(line, batch):

	basis, created = Basis.objects.update_or_create(
		internal_name=line.get('internal_name', ''),
		defaults={
			"name": line.get("name", ""),
			"acronym": line.get("acronym", ""),
			"url": line.get("url", ""),
			"description": line.get("description", ""),
			"citation": line.get("citation", ""),
			"contact": line.get("contact", ""),
			"batch": batch,
		},
	)
	author_names = line.get('authors', [])
	if created and author_names:

		if author_names:

			for author_name in author_names:
				authors = get_or_create_authorship(author_name, batch)
				basis.authors.set(authors)


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

			self.stdout.write(self.style.SUCCESS(f"Successfully created sources"))

		except Exception as e:
			print(traceback.format_exc())
			raise e
