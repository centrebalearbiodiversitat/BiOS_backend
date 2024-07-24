from django import forms
from common.utils.forms import TranslateForm, IdFieldForm
from .models import Source


class SourceForm(IdFieldForm, TranslateForm):
	origin = forms.CharField(required=False)
	name = forms.CharField(required=False)
	unidecode_name = forms.CharField(required=False)
	synonyms = forms.CharField(required=False)
	accepted = forms.BooleanField(required=False)
	accepted_modifier = forms.CharField(required=False)

	CHOICES_FIELD = {
		"origin": Source.TRANSLATE_CHOICES,
	}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


class OriginSourceForm(IdFieldForm, TranslateForm):
	origin_id = forms.IntegerField(required=False)
	source = forms.CharField(required=False)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def validate_unique(self):
		return
