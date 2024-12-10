from django import forms
from common.utils.forms import TranslateForm, IdFieldForm
from .models import Source


class SourceForm(IdFieldForm, TranslateForm):
	origin = forms.CharField(required=False)
	name = forms.CharField(required=False)
	data_type = forms.CharField(required=False)
	accepted = forms.NullBooleanField(required=False)

	CHOICES_FIELD = {
		"origin": Source.TRANSLATE_CHOICES,
		"data_type": Source.TRANSLATE_DATA_TYPE,
	}


class OriginSourceForm(IdFieldForm, TranslateForm):
	origin_id = forms.IntegerField(required=False)
	source = forms.CharField(required=False)
