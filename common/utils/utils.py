import re
import string
from apps.versioning.models import Source, Basis
SOURCE = "source"
SOURCE_TYPE = "source_type"

PUNCTUATION_TRANSLATE = str.maketrans(string.punctuation, "\n" * len(string.punctuation))


def str_clean_up(input_string):
	return re.sub(r"\s\s+", " ", input_string.replace("\u00a0", "")).strip()

def get_or_create_source(source_type, extraction_method, data_type, batch, internal_name):
	if not internal_name:
		raise Exception(f"All records must have a basis\n")
	basis, _ = Basis.objects.get_or_create(
		internal_name__iexact=internal_name,
		defaults={
			"internal_name": internal_name,
			"batch": batch
		},
	)

	source, _ = Source.objects.get_or_create(
		basis=basis,
		data_type=data_type,
		defaults={
			"source_type": source_type,
			"extraction_method": extraction_method,
			"data_type": data_type,
			"batch": batch
		},
	)

	return source

class EchoWriter:
	"""
	An object that implements just the write method of the file-like
	interface.
	"""

	def write(self, value):
		return value
