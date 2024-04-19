import re


def str_clean_up(input_string):
	return re.sub(r"\s\s+", " ", input_string.strip())