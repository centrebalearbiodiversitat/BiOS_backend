import re


def str_clean_up(input_string):
	return re.sub(r"\s\s+", " ", input_string.replace("\u00A0", "")).strip()