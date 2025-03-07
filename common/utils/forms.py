from django import forms
from humps import decamelize

from apps.API.exceptions import CBBAPIException


class IdFieldForm(forms.Form):
	id = forms.IntegerField(required=False)


class TaxonomyForm(forms.Form):
	taxonomy = forms.IntegerField(required=False)


class PaginatorFieldForm(forms.Form):
	page = forms.IntegerField(required=False, min_value=1, initial=1)

	def clean_page(self):
		value = self.cleaned_data.get("page")

		return self.fields["page"].initial if value is None else value

	@staticmethod
	def get_page(data):
		paginator_form = PaginatorFieldForm(data=data)
		if not paginator_form.is_valid():
			raise CBBAPIException(paginator_form.errors, code=400)

		return paginator_form.cleaned_data.get("page")


class CamelCaseForm(forms.Form):
	TRANSLATE_FIELDS = {}

	def __init__(self, data, *args, **kwargs):
		pre_parsed_data = {}

		for key, value in data.items():
			snake_key = decamelize(key)
			translated_key = self.TRANSLATE_FIELDS.get(snake_key, snake_key)
			pre_parsed_data[translated_key] = value

		kwargs["data"] = pre_parsed_data

		super().__init__(*args, **kwargs)


class InGeographyScopeForm(CamelCaseForm):
	in_geography_scope = forms.NullBooleanField(required=False, initial=None)


class TranslateForm(CamelCaseForm):
	CHOICES_FIELD = {}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		if hasattr(self, "data"):
			for field, translate in self.CHOICES_FIELD.items():
				if field in self.data and self.data[field]:
					self.data[field] = self.data[field].lower()

					if self.data[field] not in translate:
						raise CBBAPIException(f"Invalid {field}", 400)

					self.data[field] = translate[self.data[field]]
