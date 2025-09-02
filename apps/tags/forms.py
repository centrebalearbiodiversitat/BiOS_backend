import re

from django import forms
from common.utils.forms import TranslateForm, CamelCaseForm
from .models import IUCNData
from ..API.exceptions import CBBAPIException


class DirectiveForm(CamelCaseForm):
	cites = forms.BooleanField(required=False)
	ceea = forms.BooleanField(required=False)
	lespre = forms.BooleanField(required=False)
	directiva_aves = forms.BooleanField(required=False)
	directiva_habitats = forms.BooleanField(required=False)


class HabitatForm(forms.Form):
	habitat = forms.CharField(max_length=50, required=False)


class IUCNDataForm(TranslateForm):
	assessment = forms.CharField(max_length=50, required=False)
	region = forms.CharField(max_length=100, required=False)

	CHOICES_FIELD = {
		"assessment": IUCNData.TRANSLATE_CS,
		"region": IUCNData.TRANSLATE_RG,
	}

	def clean(self):
		cleaned_data =  super().clean()

		if (cleaned_data.get("assessment") == '') != (cleaned_data.get("region") == ''):
			raise CBBAPIException("Assessment or Region must be specified.", 400)

		return cleaned_data


class TaxonTagForm(CamelCaseForm):
	tag = forms.CharField(required=False)


class SystemForm(CamelCaseForm):
	freshwater = forms.BooleanField(required=False)
	marine = forms.BooleanField(required=False)
	terrestrial = forms.BooleanField(required=False)
