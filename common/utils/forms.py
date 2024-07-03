from django import forms
from humps import decamelize


class IdFieldForm(forms.Form):
	id = forms.IntegerField(required=False)


class CamelCaseForm(forms.Form):
	TRANSLATE_FIELDS = {}

	def __init__(self, *args, **kwargs):
		if "data" in kwargs:
			pre_parsed_data = {}

			for key, value in kwargs["data"].items():
				snake_key = decamelize(key)
				translated_key = self.TRANSLATE_FIELDS.get(snake_key, snake_key)
				pre_parsed_data[translated_key] = value

			kwargs["data"] = pre_parsed_data

		super().__init__(*args, **kwargs)


class TranslateForm(CamelCaseForm):
	CHOICES_FIELD = {}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		if hasattr(self, "data"):
			for field, translate in self.CHOICES_FIELD.items():
				if field in self.data and self.data[field]:
					self.data[field] = self.data[field].lower()

					if self.data[field] not in translate:
						raise forms.ValidationError(f"Invalid {field}")

					self.data[field] = translate[self.data[field]]
