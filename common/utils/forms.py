from django import forms
from humps import decamelize


class CamelCaseForm(forms.ModelForm):
	TRANSLATE_FIELDS = {}

	def __init__(self, *args, **kwargs):
		if 'data' in kwargs:
			pre_parsed_data = {}
			for key, value in kwargs['data'].items():
				pre_parsed_data[decamelize(CamelCaseForm.TRANSLATE_FIELDS.get(key, key))] = value
			kwargs['data'] = pre_parsed_data
		super(CamelCaseForm, self).__init__(*args, **kwargs)
