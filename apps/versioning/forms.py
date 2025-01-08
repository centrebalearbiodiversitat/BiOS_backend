from django import forms
from common.utils.forms import TranslateForm, IdFieldForm
from .models import Source


class BasisForm(IdFieldForm, TranslateForm):
	acronym = forms.CharField(max_length=100, required=False)
	name = forms.CharField(required=False)
	# url = forms.URLField(required=False)
	# description = forms.CharField(required=False)
	# authors = forms.CharField(required=False)
	# citation = forms.CharField(required=False)


class SourceForm(IdFieldForm, TranslateForm):
	source_type = forms.CharField(required=False)
	extraction_method = forms.CharField(required=False)
	data_type = forms.CharField(required=False)

	CHOICES_FIELD = {
		"source_type": Source.TRANSLATE_SOURCE_TYPE,
		"extraction_method": Source.TRANSLATE_EXTRACTION_METHOD,
		"data_type": Source.TRANSLATE_DATA_TYPE,
	}


class OriginIdForm(IdFieldForm, TranslateForm):
	external_id = forms.IntegerField(required=False)
	source = forms.CharField(required=False)
