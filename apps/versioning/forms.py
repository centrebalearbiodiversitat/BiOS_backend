from django import forms
from common.utils.forms import TranslateForm, IdFieldForm
from .models import Source, Basis


class BasisForm(IdFieldForm, TranslateForm):
	acronym = forms.CharField(max_length=100, required=False)
	name = forms.CharField(required=False)
	type = forms.CharField(required=False)
	# url = forms.URLField(required=False)
	# description = forms.CharField(required=False)
	exact = forms.BooleanField(required=False)
	# authors = forms.CharField(required=False)
	# citation = forms.CharField(required=False)

	CHOICES_FIELD = {
		"type": Basis.TRANSLATE_TYPE,
	}

	def clean(self):
		cleaned_data = super().clean()
		if "exact" not in self.data:
			del cleaned_data["exact"]
		return cleaned_data


class SourceForm(IdFieldForm, TranslateForm):
	extraction_method = forms.CharField(required=False)
	data_type = forms.CharField(required=False)

	CHOICES_FIELD = {
		"extraction_method": Source.TRANSLATE_EXTRACTION_METHOD,
		"data_type": Source.TRANSLATE_DATA_TYPE,
	}


class OriginIdForm(IdFieldForm, TranslateForm):
	external_id = forms.IntegerField(required=False)
	source = forms.CharField(required=False)
