import re
import string
from apps.versioning.models import Module, Source

SOURCE = "source"
SOURCE_TYPE = "source_type"

PUNCTUATION_TRANSLATE = str.maketrans(string.punctuation, "\n" * len(string.punctuation))


def str_clean_up(input_string):
	return re.sub(r"\s\s+", " ", input_string.replace("\u00a0", "")).strip()


def get_or_create_module(source_type, extraction_method, data_type, batch, internal_name):
	if not internal_name:
		raise Exception(f"All records must have a source\n")

	source = Source.objects.get(
		internal_name__iexact=internal_name,
	)

	module, created = Module.objects.get_or_create(
		source=source,
		data_type=Module.TRANSLATE_DATA_TYPE[data_type],
		defaults={
			"source_type": Module.TRANSLATE_SOURCE_TYPE[source_type],
			"extraction_method": Module.TRANSLATE_EXTRACTION_METHOD[extraction_method],
			"data_type": Module.TRANSLATE_DATA_TYPE[data_type],
			"batch": batch,
		},
	)

	return module


class EchoWriter:
	"""
	An object that implements just the write method of the file-like
	interface.
	"""

	def write(self, value):
		return value
