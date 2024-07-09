import re


def str_clean_up(input_string):
	return re.sub(r"\s\s+", " ", input_string.replace("\u00a0", "")).strip()


class EchoWriter:
	"""
	An object that implements just the write method of the file-like
	interface.
	"""

	def write(self, value):
		return value
