import re
import string
from apps.versioning.models import Source, Basis, OriginId

from django.apps import apps
from django.db.models import ForeignKey
from django.http import HttpResponse
import csv

PUNCTUATION_TRANSLATE = str.maketrans(string.punctuation, "\n" * len(string.punctuation))


def str_clean_up(input_string: str) -> str:
	"""
	Clean up a string by removing extra whitespace and non-breaking spaces.

	Args:
		input_string (str): The string to clean.

	Returns:
		str: The cleaned string with normalized spaces.
	"""
	return re.sub(r"\s\s+", " ", input_string.replace("\u00a0", "")).strip()


def remove_from_keys(d: dict, substring: str) -> dict:
	"""
	Remove a specified substring from the keys of a dictionary.

	Args:
		d (dict): The original dictionary whose keys will be modified.
		substring (str): The substring to remove from each key.

	Returns:
		dict: A new dictionary with the specified substring removed from keys.
		Values are unchanged.
	"""

	return {k.replace(substring, ""): v for k, v in d.items()}


def generate_csv(data, filename="data.csv", fieldnames: list = None):
	"""
	Generate a downloadable CSV file from a list of flattened dictionaries using Django's HttpResponse.

	This function is designed to be used in a Django view. It takes a list of dictionaries (e.g.,
	after flattening nested data), determines all unique keys across those dictionaries, and creates
	a CSV file that is returned as an HTTP response for download.

	Args:
		data (list of dict): The data to be written into the CSV file.
		filename (str, optional): The name of the file to be downloaded. Defaults to "data.csv".
		fieldnames (str, optional): Names of the fields in the CSV file. Defaults to None.

	Returns:
		HttpResponse: A Django HttpResponse object with CSV content and appropriate headers for download.
	"""

	response = HttpResponse(content_type="text/csv")
	response["Content-Disposition"] = f'attachment; filename="{filename}"'

	if data:
		if not fieldnames:
			# Default to the first row’s keys in order if not provided
			fieldnames = list(data[0].keys())

		writer = csv.DictWriter(response, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(data)

	return response


def get_or_create_source(source_type, extraction_method, data_type, batch, internal_name, url=None, basis_type=None):
	if not internal_name:
		raise ValueError("All records must have a basis\n")

	basis_lookup = {"internal_name__iexact": internal_name.strip()}
	basis_defaults = {
		"type": Basis.TRANSLATE_TYPE[source_type],
		"internal_name": internal_name,
		"batch": batch,
	}

	if basis_type is not None:
		basis_lookup["type"] = basis_type

	try:
		basis, _ = Basis.objects.get_or_create(**basis_lookup, defaults=basis_defaults)
	except Basis.MultipleObjectsReturned:
		raise ValueError(f"Multiple Basis found for internal name: '{internal_name}'")

	source, _ = Source.objects.get_or_create(
		basis=basis,
		data_type=data_type,
		defaults={
			"url": url,
			"extraction_method": extraction_method,
			"batch": batch,
		},
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


def flatten_row(data: list, keys_to_flatten: list):
	"""
	Flatten specified nested list fields in a list of dictionaries into a flat list of dictionaries.

	For each dictionary in the input list `data`, this function looks for keys in
	`keys_to_flatten`. If the value at one of those keys is a list of dictionaries,
	it expands each dictionary in that list into separate flattened dictionaries,
	merging nested dict keys into the parent dictionary with prefixed keys.

	Nested dictionaries inside those lists are further flattened by joining keys
	with underscores.

	Args:
		data (list of dict): List of dictionaries to be flattened.
		keys_to_flatten (list of str): Keys whose values are nested lists to flatten.

	Returns:
		list of dict: A flattened list of dictionaries with nested list items expanded
					  and nested dict keys joined with prefixed keys.
	"""
	flattened_data = []

	for item in data:
		partial_results = [item.copy()]  # start with original item

		for key in keys_to_flatten:
			temp_results = []

			for base in partial_results:
				nested_items = base.pop(key, [])

				if not nested_items:
					temp_results.append(base.copy())
					continue

				for nested in nested_items:
					new_item = base.copy()
					for k, v in nested.items():
						if isinstance(v, dict):
							new_item.update({f"{key}_{k}_{nk}": nv for nk, nv in v.items()})
						else:
							new_item[f"{key}_{k}"] = str(v) if isinstance(v, list) else v
					temp_results.append(new_item)

			partial_results = temp_results

		flattened_data.extend(partial_results)

	return flattened_data


def flatten_columns(data: list, keys_to_flatten: list):
	"""
	Flatten specified nested dictionary or list fields in a list of dictionaries.

	Args:
		data (list of dict): List of dictionaries to be flattened.
		keys_to_flatten (list of str): Keys whose nested dictionary or list values will be flattened.

	Returns:
		list of dict: A new list of dictionaries with specified nested fields flattened.
	"""

	flattened_data = []

	for item in data:
		flat_item = item.copy()

		for key in keys_to_flatten:
			nested = flat_item.pop(key, None)

			if isinstance(nested, dict):
				# Add nested dict keys with prefix
				for k, v in nested.items():
					flat_item[f"{key}_{k}"] = v

			elif isinstance(nested, list):
				if nested and all(isinstance(el, dict) for el in nested):
					# Merge each dict in list with indexed keys
					for i, el in enumerate(nested):
						for k, v in el.items():
							flat_item[f"{key}_{i}_{k}"] = v
				else:
					# Non-dict list or empty list — store as-is or stringified
					flat_item[key] = str(nested)

			else:
				# If not a dict or list, store as-is
				flat_item[key] = nested

		flattened_data.append(flat_item)

	return flattened_data
