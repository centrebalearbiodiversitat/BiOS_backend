import re
import string
from apps.versioning.models import Source, Basis, OriginId
from django.core.exceptions import MultipleObjectsReturned
from django.apps import apps
from django.db.models import ForeignKey

PUNCTUATION_TRANSLATE = str.maketrans(string.punctuation, "\n" * len(string.punctuation))


def str_clean_up(input_string):
	return re.sub(r"\s\s+", " ", input_string.replace("\u00a0", "")).strip()


def get_or_create_source(source_type, extraction_method, data_type, batch, internal_name, url=None):
	if not internal_name:
		raise ValueError("All records must have a basis\n")

	basis, _ = Basis.objects.get_or_create(
		internal_name__iexact=internal_name.lower(),
		defaults={"internal_name": internal_name, "batch": batch},
	)

	source, _ = Source.objects.get_or_create(
		basis=basis,
		data_type=data_type,
		defaults={"url": url, "source_type": source_type, "extraction_method": extraction_method, "batch": batch},
	)

	return source


def get_or_create_source_with_dataset_key(internal_name, dataset_key, batch):
	try:
		data_type = Source.TRANSLATE_DATA_TYPE["dataset_key"]

		source = Source.objects.get(basis__internal_name__iexact=internal_name.lower(), data_type=data_type)

		if source:
			os, _ = OriginId.objects.get_or_create(
				source=source,
				external_id=dataset_key,
			)

			return os
		else:
			print(f"No Source found with internal_name '{internal_name}' and data_type 'dataset_key'.")
			return None
	except Source.DoesNotExist:
		print(f"Error: No Source found with internal_name '{internal_name}' and data_type 'dataset_key'.")
		return None


def is_batch_referenced(batch):
	"""
	Check if the given Batch instance is referenced by any model dynamically.
	"""
	for model in apps.get_models():
		for field in model._meta.get_fields():
			if isinstance(field, ForeignKey) and field.related_model == batch.__class__:
				# Check if there is any related instance pointing to this batch
				if model.objects.filter(**{field.name: batch}).exists():
					return

	batch.delete()


class EchoWriter:
	"""
	An object that implements just the write method of the file-like
	interface.
	"""

	def write(self, value):
		return value
