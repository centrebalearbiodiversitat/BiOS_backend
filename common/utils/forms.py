from django import forms
from humps import decamelize


class IdFieldForm(forms.ModelForm):
	id = forms.IntegerField(required=False)


class CamelCaseForm(forms.ModelForm):
	TRANSLATE_FIELDS = {}

	def __init__(self, *args, **kwargs):
		if "data" in kwargs:
			pre_parsed_data = {}

			for key, value in kwargs["data"].items():
				snake_key = decamelize(key)
				translated_key = self.TRANSLATE_FIELDS.get(snake_key, snake_key)
				pre_parsed_data[translated_key] = value

			kwargs["data"] = pre_parsed_data
		super(CamelCaseForm, self).__init__(*args, **kwargs)


class TranslateForm(CamelCaseForm):
	CHOICES_FIELD = {}

	def clean(self):
		cleaned_data = super().clean()
		for field, translate in self.CHOICES_FIELD.items():
			if field in cleaned_data and cleaned_data[field]:
				cleaned_data[field] = cleaned_data[field].lower()

				if cleaned_data[field] not in translate:
					raise forms.ValidationError(f"Invalid {field}")

				cleaned_data[field] = translate[cleaned_data[field]]
		return cleaned_data
