from datetime import datetime
from django import forms
from django.forms import ModelForm
from common.utils.models import SynonymModel
from common.utils.forms import TranslateForm, IdFieldForm
from .models import Source, Batch, OriginSource


class SourceForm(IdFieldForm, TranslateForm):
	origin = forms.CharField(required=False)
	CHOICES_FIELD = {
		"origin": Source.TRANSLATE_CHOICES,
	}

	class Meta:
		model = Source
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["origin"].required = False
		self.fields["name"].required = False
		self.fields["unidecode_name"].required = False
		self.fields["synonyms"].required = False
		self.fields["accepted"].required = False
		self.fields["accepted_modifier"].required = False


class OriginSourceForm(IdFieldForm,TranslateForm):
	class Meta:
		model = OriginSource
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["origin_id"].required = False
		self.fields["source"].required = False

	def validate_unique(self):
		return
