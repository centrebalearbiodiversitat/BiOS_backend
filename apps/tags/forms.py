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


class IUCNDataForm(TranslateForm):
	iucn_global = forms.CharField(max_length=100, required=False)
	iucn_europe = forms.CharField(max_length=100, required=False)
	iucn_mediterranean = forms.CharField(max_length=100, required=False)
	habitat = forms.IntegerField(required=False)

	CHOICES_FIELD = {
		"iucn_global": IUCNData.TRANSLATE_CS,
		"iucn_europe": IUCNData.TRANSLATE_CS,
		"iucn_mediterranean": IUCNData.TRANSLATE_CS,
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
