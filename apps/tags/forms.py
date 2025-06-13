from django import forms

from common.utils.forms import TranslateForm, CamelCaseForm

from .models import IUCNData


class DirectiveForm(CamelCaseForm):
	cites = forms.BooleanField(required=False)
	ceea = forms.BooleanField(required=False)
	lespre = forms.BooleanField(required=False)
	directiva_aves = forms.BooleanField(required=False)
	directiva_habitats = forms.BooleanField(required=False)

	class Meta:
		fields = "__all__"


class HabitatForm(TranslateForm):
	habitat = forms.CharField(max_length=50, required=False)


class IUCNDataForm(TranslateForm):
	assessment = forms.CharField(max_length=50, required=False)
	region = forms.CharField(max_length=100, required=False)

	CHOICES_FIELD = {
		"assessment": IUCNData.TRANSLATE_CS,
		"region": IUCNData.TRANSLATE_RG,
	}


class TaxonTagForm(CamelCaseForm):
	tag = forms.CharField(required=False)

	class Meta:
		fields = ["taxonomy", "tag"]


class SystemForm(CamelCaseForm):
	freshwater = forms.BooleanField(required=False)
	marine = forms.BooleanField(required=False)
	terrestrial = forms.BooleanField(required=False)

	class Meta:
		fields = ["taxonomy", "freshwater", "marine", "terrestrial"]
